from src.models import RetrieverToolSpec
from .prompts import (
    SEMIS2_INSTRUCTION_PROMPT,
    SEMIS2_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.core.tools.constants import SEARCH_CONFIG, CITATION_FIELD_MAPPINGS_ROW


tool_spec = RetrieverToolSpec(
    tool_name="semis2_retriever",
    index_name= "index-oai-semis2-alias",
    prompts={
        "instruction_prompt": (
            "SEMIS2_INSTRUCTION_PROMPT",
            SEMIS2_INSTRUCTION_PROMPT,
        ),  
        "tool_description_prompt": (
            "SEMIS2_TOOL_DESCRIPTION_PROMPT",
            SEMIS2_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config=SEARCH_CONFIG,
    citation_field_mappings=CITATION_FIELD_MAPPINGS_ROW
)

semis2_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)