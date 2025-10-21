from src.models import RetrieverToolSpec
from .prompts import (
    P2F_INSTRUCTION_PROMPT,
    P2F_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool

tool_spec = RetrieverToolSpec(
    tool_name="p2f_retriever",
    index_name="index-oai-p2f-poc",
    prompts={
        "instruction_prompt": (
            "P2F_INSTRUCTION_PROMPT",
            P2F_INSTRUCTION_PROMPT,
        ),  
        "tool_description_prompt": (
            "P2F_TOOL_DESCRIPTION_PROMPT",
            P2F_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config={
        "search": "query-to-be-replaced-by-retriever",
        "queryType": "semantic",
        "semanticConfiguration": "oai-semantic-config",
        "captions": "extractive",
        "answers": "extractive|count-3",
        "queryLanguage": "en-US",
        "top": 5,
    }
)

p2f_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)