import asyncio

from pydantic import BaseModel
from typing import Optional, Type, List
from dotenv import load_dotenv

load_dotenv(override=True)

from azure.ai.agents import AgentsClient
from azure.ai.agents.models import MessageRole, ListSortOrder
from tenacity import retry, stop_after_attempt, wait_exponential

from src.core.base import LamBotTool
from src.models import ToolType
from src.clients import LifespanClients
from src.models.azure_ai_foundry_agent_tool import (
    AIFoundryAgentInput,
    AIFoundryAgentToolSpec
)
from src.models.intermediate_step import IntermediateStep

def custom_retry_message(retry_state):
    print(f"Retrying AzureAIFoundryTool _execute... Attempt {retry_state.attempt_number}. Exception: {retry_state.outcome.exception()}")


class AzureAIFoundryTool(LamBotTool):
    """
    LamBot wrapper for the Azure AI Foundry Agent tool.
    """

    args_schema: Type[BaseModel] = AIFoundryAgentInput
    tool_spec: AIFoundryAgentToolSpec
    agent_client: AgentsClient = None
    created_fallback_agent: bool = False
    tools: Optional[List] = None
    thread_id: Optional[str] = None

    def __init__(self, tool_spec: AIFoundryAgentToolSpec):
        super().__init__(
            name=tool_spec.tool_name,
            description=tool_spec.tool_description_prompt,
            tool_type=ToolType.non_retriever_tool,
            tool_spec=tool_spec,
        )
        self.agent_client = (
            LifespanClients.get_instance().azure_ai_foundry_agent.agent_client
        )
        self.created_fallback_agent = False
        self.tools = self._configure_tool()
        self.thread_id = None

    @classmethod
    def from_tool_spec(cls, spec: AIFoundryAgentToolSpec):
        return cls(tool_spec=spec)

    @classmethod
    def _configure_tool(cls):
        return []

    def _get_or_create_agent(self) -> str:
        """
        Fetch the agent by ID or create a new one if it doesn't exist.
        """

        try:
            agent = self.agent_client.get_agent(self.tool_spec.agent_id)
        except Exception as e:
            # If agent retrieval fails, create a new agent
            agent = self.agent_client.create_agent(
                model="gpt-4o",
                name=self.tool_spec.agent_name,
                instructions=self.tool_spec.agent_system_message,
                tools=self.tools,
                temperature=0.0,
            )

            self.created_fallback_agent = True
            print(
                f"Created fallback agent with ID {agent.id} due to retrieval failure: {e}"
            )
        return agent.id

    @retry(
        stop=stop_after_attempt(3),  # Retry up to 3 times
        wait=wait_exponential(multiplier=1, min=2, max=6),  # Exponential backoff: 2s, 4s, 6s
        before_sleep=custom_retry_message,
    )
    def _execute(self, query_str: str) -> tuple[str, str]:
        """
        Shared logic used by both sync and async functions.
        """
        thread = self.agent_client.threads.create()
        thread_id = thread.id
        self.agent_client.messages.create(
            thread_id=thread_id, role="user", content=query_str
        )

        agent_id = self._get_or_create_agent()
        run = self.agent_client.runs.create_and_process(
            thread_id=thread_id,
            agent_id=agent_id,
            tool_choice={"type": self.tool_spec.ai_foundry_tool_name},  # fixed per requirements
            parallel_tool_calls=False,
            max_completion_tokens=2000,
            temperature=0.0,
        )

        if run.status == "failed":
            raise RuntimeError(f"Agent failed: {run.last_error}")

        # Grab the assistant’s final message
        messages = self.agent_client.messages.list(
            thread_id=thread_id, order=ListSortOrder.ASCENDING
        )

        answer_chunks = [
            m.text_messages[-1].text.value
            for m in messages
            if m.role == MessageRole.AGENT and m.text_messages
        ]
        answer = "\n".join(answer_chunks)

        if self.created_fallback_agent:
            self.agent_client.delete_agent(agent_id)
            print(f"Fallback agent with ID {agent_id} deleted it after use.")

        return answer, thread_id
    
    def _dispatch_initial_intermediate_step(self, query: AIFoundryAgentInput):
        self.dispatch_intermediate_step(
            intermediate_step=IntermediateStep(
                message=f"Running Azure AI Foundry tool with query: {query}"
            )
        )

    def _run(self, query: AIFoundryAgentInput) -> str:
        self._dispatch_initial_intermediate_step(query)
        return self._execute(query)

    async def _arun(self, query: AIFoundryAgentInput) -> str:
        self._dispatch_initial_intermediate_step(query)
        # Run blocking _execute in a background thread so we don't block the event loop
        return await asyncio.to_thread(self._execute, query)
