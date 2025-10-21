from src.models import RetrieverToolSpec
from src.core.tools.community.etch_redacted_retriever.prompts import (
    REDACTED_ETCH_INSTRUCTION_PROMPT,
    REDACTED_ETCH_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.core.tools.constants import SEARCH_CONFIG, CITATION_FIELD_MAPPINGS_ROW


tool_spec = RetrieverToolSpec(
    tool_name="etch_redacted_retriever",
    index_name="index-oai-etch-redacted-alias",
    prompts={
        "instruction_prompt": (
            "REDACTED_ETCH_INSTRUCTION_PROMPT",
            REDACTED_ETCH_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "REDACTED_ETCH_TOOL_DESCRIPTION_PROMPT",
            REDACTED_ETCH_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config=SEARCH_CONFIG,
    citation_field_mappings=CITATION_FIELD_MAPPINGS_ROW,
)

etch_redacted_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
