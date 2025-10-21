import os
from dotenv import load_dotenv

load_dotenv(override=True)

from langchain_core.tools import BaseTool
from langchain_openai import AzureChatOpenAI
from src.models import LamBotConfig, QueryConfig
from src.core.tools.registry import get_tool_by_name
from src.models.request import MessageFile
from src.models import ToolType
from src.core.base import Helper, LamBotTool
from src.core.utils.query_config_utils import enhance_system_message_with_user_context
from src.core.utils.ms_graph_utils import get_user_graph_info
from typing import List, Optional, Dict, Any, Tuple
from langchain_core.prompts.prompt import PromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
    ChatPromptTemplate
)
from langchain_community.adapters.openai import convert_openai_messages
from langchain.tools import tool
from src.core.tools.common.retriever import LamBotMultiRetrieverTool, LamBotRetrieverTool
from src.core.bots.utils import create_multiretriever_tool_spec
from src.models.constants import LLMFeature
from src.models.config import AzureOpenAIRegion
from src.core.agents.common import DeepResearchAgentV2
from src.clients import LifespanClients
from src.models.constants import IntakeItem
from src.clients.azure import openai_token_provider
from src.core.database.lambot import LamBotMongoDB

llm_config_service = LamBotMongoDB.get_instance().language_model_config_db


@tool
def dummy_tool(input: str) -> str:
    """Do not call this tool. It is a dummy tool and returns nothing"""
    return ""


class LamBot(Helper):
    def __init__(self, bot_config: LamBotConfig, query_config: QueryConfig, file_attachments: Optional[List[MessageFile]] = None):
        """
        Initialize the Bot with the given configuration.

        Args:
            bot_config (LamBotConfig): Configuration for the bot.
        """
        super().__init__(
            lambot_config=bot_config
        )  # Initialize the Step class with the bot's display name

        self.bot_config = bot_config
        self._query_config = query_config or bot_config.default_query_config
        self._llm: Optional[AzureChatOpenAI] = None
        self._chat_history = None
        self._agent: Optional[create_tool_calling_agent] = None
        self._agent_executor: Optional[AgentExecutor] = None
        self._file_attachments = file_attachments or []
        self.lambot_system_message: Optional[str] = None
        self.intake_flags = None

        self.configure(self._query_config)


    def configure(self, query_config: QueryConfig) -> None:
        """
        Configure LLM, tools, and agent based on the query config.

        Args:
            query_config (QueryConfig): The configuration to apply to the bot.
        """
        self.apply_query_config(query_config)

        self._configure_llm()
        self._configure_tools()
        self._configure_agent()

        
    def apply_query_config(self, query_config: QueryConfig) -> None:
        """
        Apply the query configuration to the bot.

        Args:
            query_config (QueryConfig): The configuration to apply.
        """
        # Convert default_query_config to a dictionary
        default_config_dict = self.bot_config.default_query_config.model_dump()

        # Iterate over each attribute in the default_query_config
        for field, default_value in default_config_dict.items():
            # If the value in query_config is None, replace it with the value from _default_query_config
            if getattr(query_config, field) is None:
                setattr(query_config, field, default_value)

        # Update self._query_config with the new values
        self._query_config = query_config

        # Check if the selected tools are a subset of the configured tools
        if not set(self._query_config.selected_tools).issubset(self.bot_config.tools):
            raise ValueError(
                "One or more selected tools are not in the configured tools. "
                "Please ensure all selected tools are within the configured tools list of your LamBot."
            )
        
        self.langfuse_manager.callback_handler.metadata = self._query_config.model_dump()
        
    def _update_intake_flags(self, intake_item, value):
        """
        Updates the intake flags dictionary with the given intake item and value.

        Args:
            intake_item: The intake item to update (e.g., IntakeItem.CONVERSATION_HISTORY).
            value: The value to set for the intake item (e.g., True, False, or None).
        """
        if self.intake_flags is None:
            self.intake_flags = {}  # Create the dictionary only when needed
        self.intake_flags[intake_item] = value

    @property
    def llm(self) -> Optional[AzureChatOpenAI]:
        """
        Get the configured LLM.

        Returns:
            AzureChatOpenAI: The configured LLM.
        """
        return self._llm

    @property
    def tools(self) -> List[BaseTool]:
        """
        Get the configured tools.

        Returns:
            List[Tool]: The list of configured tools.
        """
        return self._tools

    @property
    def system_message(self) -> str:
        """
        Get the system message.

        Returns:
            str: The system message.
        """
        return self._system_message

    @property
    def temperature(self) -> float:
        """
        Get the temperature.

        Returns:
            float: The temperature setting.
        """
        return self._temperature

    @property
    def agent_executor(self) -> Optional[AgentExecutor]:
        """
        Get the agent executor.

        Returns:
            AgentExecutor: The agent executor.
        """
        return self._agent_executor

    @property
    def chat_history(self) -> None:
        """
        Get chat history

        Args:
            chat_history (List[Dict[str, Any]]): The chat history to use.
        """
        return self._chat_history
    
    @property
    def file_attachments(self):
        """Get the file attachments."""
        return self._file_attachments

    @chat_history.setter
    def chat_history(self, chat_history: List[Dict[str, Any]]) -> None:
        """
        Set chat history for prompt creation.

        Args:
            chat_history (List[Dict[str, Any]]): The chat history to use.
        """
        self._chat_history = chat_history

    def _configure_llm(self) -> None:
        """Private method to configure and instantiate the LLM."""

        # If supported models are not in llm_configs, raise an exception
        supported_models = [llm.name for llm in self.bot_config.supported_language_models]
        llm_config_models = list(llm_config_service.fetch_all_language_model_keys())

        if not set(supported_models).issubset(llm_config_models):
            raise ValueError(
                "One or more supported models are not in the llm_configs."
            )

        ll_model = self._query_config.language_model
        llm_config = llm_config_service.fetch_language_model(ll_model.name)
        
        if llm_config:
            if LLMFeature.REASONING not in llm_config.unsupported_features:
                # Prepend "Formatting re-enabled" with a line break to the system message
                self._query_config.system_message = f"Formatting re-enabled\n{self._query_config.system_message}"

            lifespan_clients = LifespanClients.get_instance()

            if llm_config.region == AzureOpenAIRegion.EastUS:
                client = lifespan_clients.azure_openai.azure_use_region_client
            elif llm_config.region == AzureOpenAIRegion.EastUS2:
                client = lifespan_clients.azure_openai.azure_use2_region_client
            else:
                raise ValueError("Unsupported Azure OpenAI region.")
        
            self._llm = AzureChatOpenAI(
                azure_ad_token_provider=openai_token_provider,
                azure_endpoint=llm_config.endpoint,
                api_version=llm_config.api_version,
                azure_deployment=llm_config.deployment_name,
                model=llm_config.name,
                seed=os.getenv("LLM_SEED", 42),
                temperature=self._query_config.temperature if LLMFeature.TEMPERATURE not in llm_config.unsupported_features else 1,
                streaming=True if LLMFeature.STREAMING not in llm_config.unsupported_features else False,
                tags=["lambot-agent-llm"],
                stream_options={"include_usage": True},
                client=client
            )
        else:
            raise ValueError("The provided LLM Spec is not supported.")

    def _supply_tool_kwargs_to_tools(self, tool: LamBotTool) -> None:
        """Private method to supply tool keyword arguments to tools."""
        tool_kwargs_by_name = getattr(self._query_config, "tool_kwargs", {})
        tool_kwargs = tool_kwargs_by_name.get(tool.name)
        tool.set_tool_kwargs(tool_kwargs)

        # For LamBotMultiRetrieverTool, also supply kwargs to sub-tools
        if isinstance(tool, LamBotMultiRetrieverTool):
            for sub_tool in tool.retriever_tools:
                sub_tool_allowed_intakes = sub_tool.allowed_intakes
                if sub_tool_allowed_intakes and IntakeItem.TOOL_KWARGS in sub_tool_allowed_intakes:
                    sub_tool.set_tool_kwargs(tool_kwargs)

    def _configure_tools(self) -> None:
        """Private method to configure and instantiate tools."""

        selected_tool_configs = [tool for tool in self._query_config.selected_tools if tool.user_has_access]

        # Initialize an empty list for tools
        self._tools = []

        # If no tools are selected, fall back to using the dummy tool
        if not selected_tool_configs:
            self._tools = [dummy_tool]
            return

        # Add each selected tool, and track retriever tools separately for later processing
        retriever_tools = []
        display_names = []
        for tool_config in selected_tool_configs:
            tool = get_tool_by_name(tool_config.name)
            allowed_intakes = tool.allowed_intakes

            if tool:
                # Inject SharePoint URLs for CustomSharePointTool
                if hasattr(tool, 'sharepoint_urls') and self.bot_config.sharepoint_urls:
                    tool.sharepoint_urls = self.bot_config.sharepoint_urls

                if hasattr(tool, 'tool_spec') and hasattr(tool.tool_spec, 'system_message_hint') and tool.tool_spec.system_message_hint:
                    if not self.lambot_system_message:
                        self.lambot_system_message = ""
                    self.lambot_system_message += f"\n{tool.tool_spec.system_message_hint}"

                # Pass file attachments to file-aware tools
                if hasattr(tool, 'file_attachments'):
                    tool.file_attachments = self._file_attachments

                if allowed_intakes:
                    for intake_item in IntakeItem:
                        if intake_item in allowed_intakes:
                            self._update_intake_flags(intake_item, True)

                    # Supply tool keyword arguments to the tool if allowed
                    if IntakeItem.TOOL_KWARGS in allowed_intakes:
                        self._supply_tool_kwargs_to_tools(tool)

                # Check if the tool is a retriever tool
                if tool.tool_type == ToolType.retriever_tool:
                    display_names.append(tool_config.display_name)
                    if isinstance(tool, LamBotMultiRetrieverTool) and self.bot_config.combine_retriever_tools and len(selected_tool_configs) > 1:
                        for sub_tool in tool.retriever_tools:
                            if not isinstance(sub_tool, LamBotRetrieverTool):
                                raise TypeError(f"Expected instance of LamBotRetrieverTool, got {type(sub_tool)} instead")
                            sub_tool.override_top_k(k=self._query_config.top_k)
                            retriever_tools.append(sub_tool)
                    else:
                        # Override the top_k value for either the single retriever tool or a multi-retriever tool (all sub-retriever-tools)
                        tool.override_top_k(k=self._query_config.top_k)
                        tool.set_display_names(display_names)
                        retriever_tools.append(tool)
                # Append the tool to the tools list
                self._tools.append(tool)
            else:
                # Raise an exception if the tool does not exist
                raise ValueError(f"Tool '{tool_config.name}' does not exist.")

        # If the combine_retriever_tools flag is set to True and there is more than one retriever tool, combine them
        # Note: Only retriever tools are combined; other non-retriever tools will stay in place.

        # Remove individual retriever tools and add the combined retriever tool
        self._tools = [
            tool
            for tool in self._tools
            if tool.tool_type != ToolType.retriever_tool
        ]
        if self.bot_config.combine_retriever_tools and len(retriever_tools) > 1:
            unique_retriever_tools = list(set(retriever_tools))
            lambot_multiretriever_tool_spec = create_multiretriever_tool_spec(prefix=self.bot_config.display_name)
            multi_retriever_tool = LamBotMultiRetrieverTool.from_tools(retriever_tools=unique_retriever_tools, tool_spec=lambot_multiretriever_tool_spec, multi_retriever_top_k=self._query_config.top_k, display_names=display_names)
            
            self._tools.append(multi_retriever_tool)
        elif len(retriever_tools) == 1:
            retriever_tool = retriever_tools[0]
            if isinstance(retriever_tool, LamBotMultiRetrieverTool):
                retriever_tool.set_display_names(display_names)
            self._tools.append(retriever_tool)
        else:
            self.logger.info("No retriever tools selected.")

    def _configure_tool_calling_agent(self) -> None:
        """Private method to configure the agent and agent executor."""
        prompt = self._create_chat_prompt(
            self._chat_history if self._chat_history else []
        )
        self._agent = create_tool_calling_agent(self._llm, self._tools, prompt)
        self._agent_executor = AgentExecutor(
            agent=self._agent, tools=self._tools, return_intermediate_steps=True, handle_parsing_errors=True
        )

    def _configure_deep_research_agent(self) -> None:
        """Private method for configuring the deep research agent."""
        self._agent = DeepResearchAgentV2()
        self._agent_executor = self._agent.graph

    def _configure_agent(self) -> None:
        """Private method to configure the agent."""
        # Check if the LLM is configured
        if not self._llm:
            raise ValueError("LLM is not configured. Please configure the LLM first.")

        # Check if tools are configured
        if not self._tools:
            raise ValueError("Tools are not configured. Please configure the tools first.")
        
        if self._query_config.deep_research.enabled:
            self._configure_deep_research_agent()
        else:
            self._configure_tool_calling_agent()

    def _create_chat_prompt(
        self, chat_history: Optional[List[Dict[str, Any]]] = None
    ) -> ChatPromptTemplate:
        """
        Creates a chat prompt template by assembling the conversation history,
        a user input prompt, and an agent scratchpad for additional context.

        The conversation history is processed from a list of messages,
        where each message is a dictionary with keys "role" and "content".
        The content can be text or image data.

        Parameters:
            chat_history (Optional[List[Dict[str, Any]]]): A list of message dictionaries.
                Each dictionary should include a "role" (e.g., "user", "assistant", "system")
                and "content" (text or image data). This parameter is optional.

        Returns:
            ChatPromptTemplate: A prompt template that includes the chat history,
            the current user input, and an agent scratchpad.
        """
        # Enhance system message with current user's context
        user_info = get_user_graph_info()
        enhanced_system_message = enhance_system_message_with_user_context(self._query_config.system_message, user_info)
        
        system_message_template = SystemMessagePromptTemplate(
            prompt=PromptTemplate(input_variables=[], template=enhanced_system_message)
        )
        chat_history_template = MessagesPlaceholder(
            variable_name="chat_history", optional=True
        ).format_messages(chat_history=convert_openai_messages(chat_history))
        
        user_input_template = HumanMessagePromptTemplate(
            prompt=PromptTemplate(input_variables=["input"], template="{input}")
        )
        
        agent_scratchpad_template = MessagesPlaceholder(
            variable_name="agent_scratchpad", optional=True
        )
        
        # Assemble and return the complete chat prompt template.
        prompt = ChatPromptTemplate.from_messages(
            [system_message_template] + chat_history_template + [user_input_template, agent_scratchpad_template]
        )

        if self.lambot_system_message:
            system_message = SystemMessagePromptTemplate(
                prompt=PromptTemplate(input_variables=[], template=self.lambot_system_message)
            )
            prompt.messages.insert(1, system_message)

        return prompt
    
    def _prepare_agent_execution(self, messages: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Prepare the agent executor input and invoke configuration.

        Args:
            messages (List[Dict[str, Any]]): The list of messages to use in the conversation.

        Returns:
            Tuple[Dict[str, Any], Dict[str, Any]]: The agent executor input and invoke configuration.
        """

        base_invoke_config = {
            "configurable": {"session_id": "<foo>"},
            "callbacks": [self.langfuse_manager.callback_handler],
            "run_id": self.metric_api_client.correlation_id
        }

        if self._query_config.deep_research.enabled:
            config = self._query_config.deep_research
            invoke_config = base_invoke_config.copy()
            invoke_config["configurable"] = config.dict()
            invoke_config["configurable"]["tools"] = self._tools
            agent_executor_input = {"messages": convert_openai_messages(messages)}
        else:
            invoke_config = base_invoke_config
            agent_executor_input = {"input": messages[-1]["content"]}

        return agent_executor_input, invoke_config