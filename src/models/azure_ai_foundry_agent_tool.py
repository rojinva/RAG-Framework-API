from src.models.base import ConfiguredBaseModel
from pydantic import Field, BaseModel
from typing import Optional
from enum import StrEnum


class AzureAIFoundryToolNames(StrEnum):
    BING_GROUNDING = "bing_grounding"
    BING_GROUNDING_CUSTOM_SEARCH = "bing_custom_search"


class BingGroundingCustomSearchInstanceNames(StrEnum):
    FINANCE = "finance"
    PAYROLL = "payroll"


class BingGroundingToolSearchMarket(StrEnum):
    US = "en-US"


class BingGroundingToolSearchLanguage(StrEnum):
    EN = "en"
    FR = "fr"
    DE = "de"
    ES = "es"
    IT = "it"


class BingGroundingToolArgs(BaseModel):
    """
    Arguments for the Bing Grounding tool.
    """

    count: int = Field(
        10, description="The number of search results to return in the response."
    )
    freshness: Optional[str] = Field(
        None,
        description="Filter search results by age (e.g., 'Day', 'Week', 'Month'). For a specific date range, use 'YYYY-MM-DD..YYYY-MM-DD'.",
    )
    market: BingGroundingToolSearchMarket = Field(
        BingGroundingToolSearchMarket.US,
        description="The market where the results come from, in the form '<language>-<country/region>'. For example, 'en-US'.",
    )
    set_lang: BingGroundingToolSearchLanguage = Field(
        BingGroundingToolSearchLanguage.EN,
        description="The language to use for user interface strings. Use a 2-letter or 4-letter code (e.g., 'en', 'fr-ca').",
    )


class BingGroundingCustomSearchToolArgs(BingGroundingToolArgs):
    """
    Arguments for the Bing Custom Search tool.
    """

    instance_name: BingGroundingCustomSearchInstanceNames = Field(
        ..., description="The instance name for the Bing Custom Search tool."
    )

class AIFoundryAgentToolSpec(ConfiguredBaseModel):
    """
    Minimal declarative config for the Azure AI Foundry Agent tool.
    """

    ai_foundry_tool_name: str = Field(..., description="Unique name for this tool defined in Azure AI Foundry.")
    tool_name: str = Field(..., description="Name of the tool for lambots to use.")
    tool_description_prompt: str = Field(
        ..., description="Prompt to describe the tool's functionality."
    )
    agent_id: str = Field(..., description="Azure Foundry Agent ID.")
    agent_name: str = Field(
        ...,
        description="Name of the agent to be created or used.",
    )
    agent_system_message: str = Field(
        ...,
        description="System message to initialize the agent with.",
    )


class BingAzureAIFoundryAgentToolSpec(AIFoundryAgentToolSpec):
    """
    Minimal declarative config for the Azure AI Foundry Agent tool.
    """

    tool_args: Optional[BingGroundingToolArgs] = Field(
        None, description="Optional arguments to pass to the agent tool."
    )


class AIFoundryAgentInput(BaseModel):
    """Input to the retriever."""

    query: str = Field(
        description="The input to the agent. This should be a well formed user query."
    )
