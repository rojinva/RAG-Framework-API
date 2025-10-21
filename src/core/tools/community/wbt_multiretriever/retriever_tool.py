from src.core.tools.common.retriever import LamBotMultiRetrieverTool
from src.models.retriever_tool import MultiRetrieverToolSpec
from .prompts import (
    WBT_MULTIRETREIVER_INSTRUCTION_PROMPT,
    WBT_MULTIRETRIEVER_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.community.cci_retrievers.wbt_cci_retriever import (
    wbt_cci_retriever_tool,
)
from src.core.tools.community.wbt_course_description_retriever import (
    wbt_course_description_retriever_tool,
)

tool_spec = MultiRetrieverToolSpec(
    tool_name="wbt_multiretriever",
    prompts={
        "instruction_prompt": (
            "WBT_MULTIRETREIVER_INSTRUCTION_PROMPT",
            WBT_MULTIRETREIVER_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "WBT_MULTIRETRIEVER_TOOL_DESCRIPTION_PROMPT",
            WBT_MULTIRETRIEVER_TOOL_DESCRIPTION_PROMPT,
        ),
    },
)

wbt_multiretriever_tool = LamBotMultiRetrieverTool.from_tools(
    retriever_tools=[
        wbt_course_description_retriever_tool,
        wbt_cci_retriever_tool,
    ],
    tool_spec=tool_spec,
    display_names=[],
)
