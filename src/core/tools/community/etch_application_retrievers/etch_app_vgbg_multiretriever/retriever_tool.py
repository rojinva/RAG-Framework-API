from src.core.tools.common.retriever import LamBotMultiRetrieverTool
from src.models.retriever_tool import MultiRetrieverToolSpec
from ..prompts import (
    ETCH_MULTIRETRIEVER_INSTRUCTION_PROMPT,
    ETCH_TOOL_DESCRIPTION_PROMPT,
)
from .etch_app_vgbg_retriever import etch_app_vgbg_retriever_tool
from .etch_app_vgbg_redacted_retriever import (
    etch_app_vgbg_redacted_retriever_tool,
)

tool_spec = MultiRetrieverToolSpec(
    tool_name="etch_app_vgbg_multiretriever",
    prompts={
        "instruction_prompt": (
            "ETCH_MULTIRETRIEVER_INSTRUCTION_PROMPT",
            ETCH_MULTIRETRIEVER_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "ETCH_TOOL_DESCRIPTION_PROMPT",
            ETCH_TOOL_DESCRIPTION_PROMPT,
        ),
    },
)

etch_app_vgbg_multiretriever_tool = LamBotMultiRetrieverTool.from_tools(
    retriever_tools=[
        etch_app_vgbg_retriever_tool,
        etch_app_vgbg_redacted_retriever_tool,
    ],
    tool_spec=tool_spec,
    display_names=[],
)
