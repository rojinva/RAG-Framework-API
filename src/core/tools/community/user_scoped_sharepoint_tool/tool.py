from src.core.tools.common.sharepoint.user_scoped_sharepoint_tool import UserScopedSharePointTool
from src.models.sharepoint_tool import SharePointToolSpec
from .prompts import (
    SHAREPOINT_INSTRUCTION_PROMPT,
    SHAREPOINT_TOOL_DESCRIPTION_PROMPT,
)
tool_name = "user_scoped_sharepoint_tool"
# SharePoint tool specification
sharepoint_tool_spec = SharePointToolSpec(
    tool_name=tool_name,
    prompts={
        "instruction_prompt": (
            "SHAREPOINT_INSTRUCTION_PROMPT",
            SHAREPOINT_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "SHAREPOINT_TOOL_DESCRIPTION_PROMPT", 
            SHAREPOINT_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    maximum_number_of_results=10,
    system_message_hint=f"Always call {tool_name} tool when the user is asking questions related to Lam Research or internal datasources. Additionally, both {tool_name} and retriever tool should be called if they are included."
)

# Initialize the SharePoint tool
user_scoped_sharepoint_tool = UserScopedSharePointTool.from_tool_spec(sharepoint_tool_spec)
