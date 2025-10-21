from src.models import RetrieverToolSpec
from .prompts import (
    RELIABILITYREPORTS_INSTRUCTION_PROMPT,
    RELIABILITYREPORTS_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.core.tools.constants import SEARCH_CONFIG, CITATION_FIELD_MAPPINGS_ROW


tool_spec = RetrieverToolSpec(
    tool_name="reliabilityreports_retriever",
    index_name= "index-oai-reliability-reports-alias",
    prompts={
        "instruction_prompt": (
            "RELIABILITYREPORTS_INSTRUCTION_PROMPT",
            RELIABILITYREPORTS_INSTRUCTION_PROMPT,
        ),  
        "tool_description_prompt": (
            "RELIABILITYREPORTS_TOOL_DESCRIPTION_PROMPT",
            RELIABILITYREPORTS_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config=SEARCH_CONFIG,
    citation_field_mappings=CITATION_FIELD_MAPPINGS_ROW
)

reliabilityreports_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)