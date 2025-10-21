from src.models import RetrieverToolSpec
from .prompts import (
    CHANGE_ORDER_VIEW_INSTRUCTION_PROMPT,
    CHANGE_ORDER_VIEW_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.models.citation import CitationTagAliasSpec

tool_spec = RetrieverToolSpec(
    tool_name="changeorderview_retriever",
    index_name="index-oai-change-order-view-alias",
    prompts={
        "instruction_prompt": (
            "CHANGE_ORDER_VIEW_INSTRUCTION_PROMPT",
            CHANGE_ORDER_VIEW_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "CHANGE_ORDER_VIEW_TOOL_DESCRIPTION_PROMPT",
            CHANGE_ORDER_VIEW_TOOL_DESCRIPTION_PROMPT,
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
    },
    citation_field_mappings={
        "ECRNUMBER": CitationTagAliasSpec(default="Change Order")
    },
)

change_order_view_retriever_tool = LamBotRetrieverTool.from_tool_spec(
    tool_spec
)
