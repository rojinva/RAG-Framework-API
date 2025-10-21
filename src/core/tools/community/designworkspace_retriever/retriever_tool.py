from src.models import RetrieverToolSpec
from .prompts import (
    DESIGNWORKSPACE_INSTRUCTION_PROMPT,
    DESIGNWORKSPACE_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool

tool_spec = RetrieverToolSpec(
    tool_name="designworkspace_retriever",
    index_name="index-oai-designworkspace-alias",
    prompts={
        "instruction_prompt": (
            "DESIGNWORKSPACE_INSTRUCTION_PROMPT",
            DESIGNWORKSPACE_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "DESIGNWORKSPACE_TOOL_DESCRIPTION_PROMPT",
            DESIGNWORKSPACE_TOOL_DESCRIPTION_PROMPT,
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

designworkspace_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
