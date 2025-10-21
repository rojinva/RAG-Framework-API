from src.models import RetrieverToolSpec
from .prompts import (
    DBV_SESSIONS_INSTRUCTION_PROMPT,
    DBV_SESSIONS_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.models.citation import CitationTagAliasSpec

tool_spec = RetrieverToolSpec(
    tool_name="DBV_sessions_retriever",
    index_name="index-oai-dt-dbv",
    prompts={
        "instruction_prompt": (
            "DBV_SESSIONS_INSTRUCTION_PROMPT",
            DBV_SESSIONS_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "DBV_SESSIONS_TOOL_DESCRIPTION_PROMPT",
            DBV_SESSIONS_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config={
        "search": "query-to-be-replaced-by-retriever",
        "vectorQueries": [{"kind": "text", "k": 5, "fields": "chunk_vector"}],
        "queryType": "semantic",
        "semanticConfiguration": "oai-semantic-config",
        "captions": "extractive",
        "answers": "extractive|count-3",
        "queryLanguage": "en-US",
        "top": 5,
    },
    citation_field_mappings={
        "row": CitationTagAliasSpec(default="Row"),
        "sheet_name": CitationTagAliasSpec(default="Session")
    }
)

dbv_sessions_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
