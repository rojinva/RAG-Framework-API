import os 

from src.core.tools.common.azure_ai_foundry.bing_grounding_custom_search_tool import BingGroundingCustomSearchTool
from src.models.azure_ai_foundry_agent_tool import BingAzureAIFoundryAgentToolSpec, AzureAIFoundryToolNames, BingGroundingCustomSearchInstanceNames, BingGroundingCustomSearchToolArgs

from dotenv import load_dotenv
load_dotenv(override=True)

spec = BingAzureAIFoundryAgentToolSpec(
    tool_name="bing_grounding_custom_search_payroll",
    ai_foundry_tool_name=AzureAIFoundryToolNames.BING_GROUNDING_CUSTOM_SEARCH,
    agent_id=os.getenv("AZURE_AI_FOUNDRY_BING_GROUNDING_CUSTOM_SEARCH_PAYROLL_AGENT_ID"),
    agent_name="lambot-bing-custom-search-payroll-agent",
    agent_system_message="You are a knowledgeable and helpful assistant specialized in providing accurate, detailed, and informative responses to questions about employee benefits offered by Lam Research. Your role is to assist users—primarily Lam Research employees or prospective employees—by clearly explaining various benefit programs, policies, eligibility criteria, and enrollment procedures. Ensure your responses are well-structured, easy to understand, and tailored to the specific nature of the user's inquiry. If the information is not available, politely suggest where the user might find official or updated details.",
    tool_description_prompt="Tool to search the Lam Benefits website using Bing to retrieve information.",
    tool_args=BingGroundingCustomSearchToolArgs(
        instance_name=BingGroundingCustomSearchInstanceNames.PAYROLL
    )
)

bing_grounding_custom_search_payroll_tool = BingGroundingCustomSearchTool.from_tool_spec(spec)


