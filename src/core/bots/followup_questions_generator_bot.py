import os
from dotenv import load_dotenv

load_dotenv(override=True)

from langchain_openai import AzureChatOpenAI
from src.core.tools.common.prompts import GENERIC_SUGGESTED_FOLLOWUP_QUESTIONS_PROMPT
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    FunctionMessage,
    AIMessageChunk,
)
from src.models.questions import SuggestedQuestions
from langchain_core.prompts import MessagesPlaceholder
from typing import List, Dict, Any, Union
from langchain_community.callbacks import get_openai_callback
from src.models.logging import TokenUsageDetails
from src.clients.langfuse import LangfuseManager
from src.core.database.lambot import LamBotMongoDB
from src.models.constants import LanguageModelName
from src.clients.azure import openai_token_provider

llm_config_service = LamBotMongoDB.get_instance().language_model_config_db


class FollowUpQuestionGeneratorBot:
    """
    A bot that generates follow-up questions based on the conversation history.
    """

    def __init__(self, lambot_display_name: str, langfuse_manager: LangfuseManager):
        """
        Initialize the FollowUpQuestionGeneratorBot

        Args:
            lambot_display_name (str): The name of the LamBot that is generating follow-up questions.
            langfuse_manager (LangfuseManager): The LangfuseManager instance to interact with Langfuse.
        """

        self.lambot_display_name = lambot_display_name
        self.langfuse_manager = langfuse_manager
        self._system_message = self.langfuse_manager.client.get_prompt(
            name="GENERIC_SUGGESTED_FOLLOWUP_QUESTIONS_PROMPT",
            label=os.getenv("LANGFUSE_PROMPT_LABEL", "dev"),
            fallback=GENERIC_SUGGESTED_FOLLOWUP_QUESTIONS_PROMPT
        ).prompt

        self._configure_llm()

    def _prepare_suggested_questions_prompt(
        self,
        messages: List[Dict[str, Any]],
        agent_executor_output: List[Union[AIMessageChunk, FunctionMessage, AIMessage]],
    ) -> List[Union[SystemMessage, HumanMessage, AIMessage, FunctionMessage]]:
        """Prepare the prompt for generating suggested follow-up questions.

        Args:
            messages (List[Dict[str, Any]]): The conversation history to generate follow-up questions from.
            agent_executor_output (List[Union[AIMessageChunk, FunctionMessage, AIMessage]]): The output from the agent executor.
        """

        system_messsage_template = SystemMessage(content=self._system_message)
        chat_history_template = MessagesPlaceholder(
            variable_name="chat_history", optional=True
        ).format_messages(chat_history=messages)

        # Remove the AIMessageChunk from the agent output. Should just contain FunctionMessage and AIMessage
        filtered_agent_executor_output = [
            item for item in agent_executor_output if not isinstance(item, AIMessageChunk)
        ]
        suggested_questions_prompt = (
            [system_messsage_template]
            + chat_history_template
            + filtered_agent_executor_output
        )

        return suggested_questions_prompt

    def _configure_llm(self) -> None:
        """Private method to configure and instantiate the LLM."""

        small_model_name = os.getenv("AZURE_SMALL_MODEL_DEPLOYMENT_NAME", LanguageModelName.GPT_4O_MINI)
        small_model_spec = llm_config_service.fetch_language_model(small_model_name)

        self._llm = AzureChatOpenAI(
            azure_ad_token_provider=openai_token_provider,
            azure_endpoint=small_model_spec.endpoint,
            api_version=small_model_spec.api_version,
            azure_deployment=small_model_spec.deployment_name,
            model=small_model_spec.name,
            temperature=0.0,
            streaming=False,
            callbacks=[self.langfuse_manager.callback_handler],
        ).with_structured_output(SuggestedQuestions)

    def generate_followup_questions(
        self,
        messages: List[Dict[str, Any]],
        agent_executor_output: List[Union[AIMessageChunk, FunctionMessage, AIMessage]],
    ) -> List[str]:
        """Generate follow-up questions from the conversation history.

        Args:
            messages (List[Dict[str, Any]]): The conversation history to generate follow-up questions from.
            agent_executor_output (List[Union[AIMessageChunk, FunctionMessage, AIMessage]]): The output from the agent executor.

        Returns:
            SuggestedQuestions (List[str]): The generated follow-up questions.
        """
        prompt = self._prepare_suggested_questions_prompt(messages, agent_executor_output)
        with get_openai_callback() as followup_questions_callback:
            followup_questions = self._llm.invoke(prompt)

        self.usage_metadata = TokenUsageDetails(
            prompt_tokens=followup_questions_callback.prompt_tokens,
            completion_tokens=followup_questions_callback.completion_tokens,
            total_tokens_used=followup_questions_callback.total_tokens,
        )
        
        return followup_questions.suggested_questions
