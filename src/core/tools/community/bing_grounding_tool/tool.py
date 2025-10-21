import os 

from src.core.tools.common.azure_ai_foundry.bing_grounding_tool import BingGroundingTool
from src.models.azure_ai_foundry_agent_tool import BingAzureAIFoundryAgentToolSpec, AzureAIFoundryToolNames, BingGroundingToolArgs, BingGroundingToolSearchLanguage, BingGroundingToolSearchMarket

from dotenv import load_dotenv
load_dotenv(override=True)

spec = BingAzureAIFoundryAgentToolSpec(
    tool_name="bing_grounding",
    ai_foundry_tool_name=AzureAIFoundryToolNames.BING_GROUNDING,
    agent_id=os.getenv("AZURE_AI_FOUNDRY_BING_GROUNDING_AGENT_ID"),
    agent_name="lambot-bing-grounding-agent",
    agent_system_message="You are a helpful agent that can search the web using Bing to retrieve information. The responses should be detailed and informative.",
    tool_description_prompt="Tool to answer the query via searching the web.",
    tool_args=BingGroundingToolArgs(
        count=10,
        market=BingGroundingToolSearchMarket.US,
        set_lang=BingGroundingToolSearchLanguage.EN,
    )
)

bing_grounding_tool = BingGroundingTool.from_tool_spec(spec)