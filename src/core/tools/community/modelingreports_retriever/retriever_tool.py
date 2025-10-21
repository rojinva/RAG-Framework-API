from src.models import RetrieverToolSpec
from .prompts import (
    MODELINGREPORTS_INSTRUCTION_PROMPT,
    MODELINGREPORTS_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.core.tools.constants import SEARCH_CONFIG, CITATION_FIELD_MAPPINGS_ROW


tool_spec = RetrieverToolSpec(
    tool_name="modelingreports_retriever",
    index_name="index-oai-modelling-reports-alias",
    prompts={
        "instruction_prompt": (
            "MODELINGREPORTS_INSTRUCTION_PROMPT",
            MODELINGREPORTS_INSTRUCTION_PROMPT,
        ),  
        "tool_description_prompt": (
            "MODELINGREPORTS_TOOL_DESCRIPTION_PROMPT",
            MODELINGREPORTS_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config=SEARCH_CONFIG,
    citation_field_mappings=CITATION_FIELD_MAPPINGS_ROW
)

modelingreports_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)