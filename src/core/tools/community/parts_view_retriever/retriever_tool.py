from src.models import RetrieverToolSpec
from .prompts import (
    PARTS_VIEW_INSTRUCTION_PROMPT,
    PARTS_VIEW_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool

tool_spec = RetrieverToolSpec(
    tool_name="partsview_retriever",
    index_name="index-oai-parts-view-alias",
    prompts={
        "instruction_prompt": (
            "PARTS_VIEW_INSTRUCTION_PROMPT",
            PARTS_VIEW_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "PARTS_VIEW_TOOL_DESCRIPTION_PROMPT",
            PARTS_VIEW_TOOL_DESCRIPTION_PROMPT,
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

parts_view_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
