from .prompts import (
    FMEA_INSTRUCTION_PROMPT,
    FMEA_TOOL_DESCRIPTION_PROMPT,
)
from .abstraction.fmea_chat_tool import LamBotFMEAChatTool , FMEAToolSpec
from src.core.tools.constants import CITATION_FIELD_MAPPINGS_ROW

BASE_SEARCH_CONFIG = {
    "search": "query-to-be-replaced-by-retriever",
    "count": True,
    "semanticConfiguration": "oai-semantic-config",
    "queryLanguage": "en-US",
    "top": 15,
}

tool_spec = FMEAToolSpec(
    tool_name="fmea_retriever",
    index_name="index-oai-fmea-alias",
    description="A tool for FMEA analysis",
    prompts={
        "instruction_prompt": (
            "FMEA_INSTRUCTION_PROMPT",
            FMEA_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "FMEA_TOOL_DESCRIPTION_PROMPT",
            FMEA_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config=BASE_SEARCH_CONFIG,
    citation_field_mappings=CITATION_FIELD_MAPPINGS_ROW,
)


fmea_retriever_tool = LamBotFMEAChatTool.from_tool_spec(tool_spec)