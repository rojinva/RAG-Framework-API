import os

from pydantic import BaseModel
from typing import Type
from dotenv import load_dotenv

load_dotenv(override=True)

from azure.ai.agents import AgentsClient
from azure.ai.agents.models import (
    BingGroundingTool,
    BingCustomSearchTool,
)

from src.clients import LifespanClients
from src.models.azure_ai_foundry_agent_tool import (
    AIFoundryAgentInput,
    BingAzureAIFoundryAgentToolSpec,
)
from src.core.tools.common.azure_ai_foundry.bing_grounding_tool import BingGroundingTool
from src.models.intermediate_step import IntermediateStep

class BingGroundingCustomSearchTool(BingGroundingTool):
    """
    LamBot wrapper for the Bing Custom Search tool in Azure AI Foundry Agent.
    """

    args_schema: Type[BaseModel] = AIFoundryAgentInput
    tool_spec: BingAzureAIFoundryAgentToolSpec
    agent_client: AgentsClient = None
    created_fallback_agent: bool = False

    def __init__(self, tool_spec: BingAzureAIFoundryAgentToolSpec):
        super().__init__(tool_spec=tool_spec)
        self.agent_client = (
            LifespanClients.get_instance().azure_ai_foundry_agent.agent_client
        )
        self.created_fallback_agent = False

    def _configure_tool(self):
        tool = BingCustomSearchTool(
            connection_id=os.getenv("BING_GROUNDING_CUSTOM_SEARCH_TOOL_CONNECTION_ID"),
            instance_name=self.tool_spec.tool_args.instance_name,
            count=self.tool_spec.tool_args.count,
            market=self.tool_spec.tool_args.market,
            set_lang=self.tool_spec.tool_args.set_lang,
            freshness=(
                self.tool_spec.tool_args.freshness
                if self.tool_spec.tool_args.freshness
                else ""
            ),
        )
        return tool.definitions
    
    def _dispatch_initial_intermediate_step(self, query: AIFoundryAgentInput):
        self.dispatch_intermediate_step(
            intermediate_step=IntermediateStep(
                message=f'Searching the web using query: \"{query}\"'
            )
        )

    @classmethod
    def from_tool_spec(cls, spec: BingAzureAIFoundryAgentToolSpec):
        return cls(tool_spec=spec)
