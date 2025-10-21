from src.models import RetrieverToolSpec
from .prompts import (
    EHS_INSTRUCTION_PROMPT,
    EHS_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool

tool_spec = RetrieverToolSpec(
    tool_name="ehs_retriever",
    index_name="index-oai-edms-engg-standards",
    prompts={
        "instruction_prompt": (
            "EHS_INSTRUCTION_PROMPT",
            EHS_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "EHS_TOOL_DESCRIPTION_PROMPT",
            EHS_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config={
        "search": "query-to-be-replaced-by-retriever",
        "vectorQueries": [{"kind": "text", "k": 5, "fields": "chunk_vector"}],
        "filter": "prefix eq 'EHS'",
        "queryType": "semantic",
        "semanticConfiguration": "oai-semantic-config",
        "captions": "extractive",
        "answers": "extractive|count-3",
        "queryLanguage": "en-US",
        "top": 5,
    },
)

ehs_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
