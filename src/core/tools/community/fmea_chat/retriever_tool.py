from src.models import RetrieverToolSpec
from .prompts import (
    FMEA_CHAT_INSTRUCTION_PROMPT,
    FMEA_CHAT_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool

tool_spec = RetrieverToolSpec(
    tool_name="fmeachat_retriever",
    index_name="index-oai-fmea-alias",
    prompts={
        "instruction_prompt": (
            "FMEA_CHAT_INSTRUCTION_PROMPT",
            FMEA_CHAT_INSTRUCTION_PROMPT,
        ),  
        "tool_description_prompt": (
            "FMEA_CHAT_TOOL_DESCRIPTION_PROMPT",
            FMEA_CHAT_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config={
        "search": "query-to-be-replaced-by-retriever",
        "queryType": "semantic",
        "semanticConfiguration": "oai-semantic-config",
        "captions": "extractive",
        "answers": "extractive|count-3",
        "queryLanguage": "en-US",
        "top": 10,
    }
)

fmea_chat_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)