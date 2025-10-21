from src.models import RetrieverToolSpec
from .prompts import (
    CFPA_INSTRUCTION_PROMPT,
    CFPA_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.core.tools.constants import SEARCH_CONFIG, CITATION_FIELD_MAPPINGS_ROW

tool_spec = RetrieverToolSpec(
    tool_name="cfpa_retriever",
    index_name="index-oai-cfpa-alias",
    prompts={
        "instruction_prompt": (
            "CFPA_INSTRUCTION_PROMPT",
            CFPA_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "CFPA_TOOL_DESCRIPTION_PROMPT",
            CFPA_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    redact_pii=False,
    search_config=SEARCH_CONFIG,
    citation_field_mappings=CITATION_FIELD_MAPPINGS_ROW
)

cfpa_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
