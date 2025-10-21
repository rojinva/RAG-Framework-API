from src.models import RetrieverToolSpec
from .prompts import (
    CORPORATEACCOUNTING_INSTRUCTION_PROMPT,
    CORPORATEACCOUNTING_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.core.tools.constants import SEARCH_CONFIG, CITATION_FIELD_MAPPINGS

tool_spec = RetrieverToolSpec(
    tool_name="corporateaccounting_retriever",
    index_name="index-oai-corporate-accounting",
    prompts={
        "instruction_prompt": (
            "CORPORATEACCOUNTING_INSTRUCTION_PROMPT",
            CORPORATEACCOUNTING_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "CORPORATEACCOUNTING_TOOL_DESCRIPTION_PROMPT",
            CORPORATEACCOUNTING_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config=SEARCH_CONFIG,
    citation_field_mappings=CITATION_FIELD_MAPPINGS,
)

corporateaccounting_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
