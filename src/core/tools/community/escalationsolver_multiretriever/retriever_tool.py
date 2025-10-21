from src.core.tools.common.retriever import LamBotMultiRetrieverTool
from src.models.retriever_tool import MultiRetrieverToolSpec
from .prompts import (
    ESCALATIONSOLVER_MULTIRETREIVER_INSTRUCTION_PROMPT,
    ESCALATIONSOLVER_MULTIRETRIEVER_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.community.cci_retrievers.escalationsolver_cci_retriever import (
    escalationsolver_cci_retriever_tool,
)
from src.core.tools.community.escalationsolver_retriever import (
    escalationsolver_retriever_tool,
)

tool_spec = MultiRetrieverToolSpec(
    tool_name="escalationsolver_multiretriever",
    prompts={
        "instruction_prompt": (
            "ESCALATIONSOLVER_MULTIRETREIVER_INSTRUCTION_PROMPT",
            ESCALATIONSOLVER_MULTIRETREIVER_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "ESCALATIONSOLVER_MULTIRETRIEVER_TOOL_DESCRIPTION_PROMPT",
            ESCALATIONSOLVER_MULTIRETRIEVER_TOOL_DESCRIPTION_PROMPT,
        ),
    },
)

escalationsolver_multiretriever_tool = LamBotMultiRetrieverTool.from_tools(
    retriever_tools=[
        escalationsolver_retriever_tool,
        escalationsolver_cci_retriever_tool,
    ],
    tool_spec=tool_spec,
    display_names=[],
)
