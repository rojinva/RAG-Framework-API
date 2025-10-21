import os 

from src.core.tools.common.azure_ai_foundry.bing_grounding_custom_search_tool import BingGroundingCustomSearchTool
from src.models.azure_ai_foundry_agent_tool import BingAzureAIFoundryAgentToolSpec, AzureAIFoundryToolNames, BingGroundingCustomSearchInstanceNames, BingGroundingCustomSearchToolArgs

from dotenv import load_dotenv
load_dotenv(override=True)

spec = BingAzureAIFoundryAgentToolSpec(
    tool_name="bing_grounding_custom_search_finance",
    ai_foundry_tool_name=AzureAIFoundryToolNames.BING_GROUNDING_CUSTOM_SEARCH,
    agent_id=os.getenv("AZURE_AI_FOUNDRY_BING_GROUNDING_CUSTOM_SEARCH_AGENT_ID"),
    agent_name="lambot-bing-grounding-custom-search-finance-agent",
    agent_system_message="You are a helpful agent that can search the web using Bing to retrieve information. The responses should be detailed and informative.",
    tool_description_prompt="Tool to search the web using Bing to retrieve information.",
    tool_args=BingGroundingCustomSearchToolArgs(
        instance_name=BingGroundingCustomSearchInstanceNames.FINANCE
    )
)

bing_grounding_custom_search_finance_tool = BingGroundingCustomSearchTool.from_tool_spec(spec)