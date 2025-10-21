from src.models import RetrieverToolSpec
from .prompts import (
    ESCALATIONSOLVER_INSTRUCTION_PROMPT,
    ESCALATIONSOLVER_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool

tool_spec = RetrieverToolSpec(
    tool_name="escalationsolver_retriever",
    index_name="index-oai-escalationsolver-alias",
    prompts={
        "instruction_prompt": (
            "ESCALATIONSOLVER_INSTRUCTION_PROMPT",
            ESCALATIONSOLVER_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "ESCALATIONSOLVER_TOOL_DESCRIPTION_PROMPT",
            ESCALATIONSOLVER_TOOL_DESCRIPTION_PROMPT,
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
    citation_field_mappings={},
)

escalationsolver_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
