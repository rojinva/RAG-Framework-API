from src.models import RetrieverToolSpec
from .prompts import (
    DESIGN_REVIEW_INSTRUCTION_PROMPT,
    DESIGN_REVIEW_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool

tool_spec = RetrieverToolSpec(
    tool_name="designreview_retriever",
    index_name="index-oai-designreview-alias",
    prompts={
        "instruction_prompt": (
            "DESIGN_REVIEW_INSTRUCTION_PROMPT",
            DESIGN_REVIEW_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "DESIGN_REVIEW_TOOL_DESCRIPTION_PROMPT",
            DESIGN_REVIEW_TOOL_DESCRIPTION_PROMPT,
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

design_review_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
