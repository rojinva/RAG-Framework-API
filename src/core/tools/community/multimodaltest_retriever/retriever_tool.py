from src.models import RetrieverToolSpec
from .prompts import (
    MULTIMODAL_INSTRUCTION_PROMPT,
    MULTIMODAL_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.core.tools.constants import SEARCH_CONFIG

tool_spec = RetrieverToolSpec(
    tool_name="multimodaltest_retriever",
    index_name="index-oai-multimodal-test-2",
    prompts={
        "instruction_prompt": (
            "MULTIMODAL_INSTRUCTION_PROMPT",
            MULTIMODAL_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "MULTIMODAL_TOOL_DESCRIPTION_PROMPT",
            MULTIMODAL_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config=SEARCH_CONFIG,
)

multimodal_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
