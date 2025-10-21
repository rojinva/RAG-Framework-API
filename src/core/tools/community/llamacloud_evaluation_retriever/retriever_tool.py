from src.models import RetrieverToolSpec
from .prompts import (
    LLAMACLOUD_EVALUATION_INSTRUCTION_PROMPT,
    LLAMACLOUD_EVALUATION_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.models.citation import CitationTagAliasSpec
from src.core.tools.constants import SEARCH_CONFIG


tool_spec = RetrieverToolSpec(
    tool_name="llamacloud_evaluation_retriever",
    index_name="llamacloud-evaluation-index-alias",
    prompts={
        "instruction_prompt": (
            "LLAMACLOUD_EVALUATION_INSTRUCTION_PROMPT",
            LLAMACLOUD_EVALUATION_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "LLAMACLOUD_EVALUATION_TOOL_DESCRIPTION_PROMPT",
            LLAMACLOUD_EVALUATION_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config=SEARCH_CONFIG,
    citation_field_mappings={
        "row": CitationTagAliasSpec(default="Page")
    }
)

llamacloud_evaluation_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
