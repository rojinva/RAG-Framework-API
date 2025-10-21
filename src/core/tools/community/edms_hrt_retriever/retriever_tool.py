from src.models import RetrieverToolSpec
from .prompts import (
    EDMSHRT_INSTRUCTION_PROMPT,
    EDMSHRT_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool

tool_spec = RetrieverToolSpec(
    tool_name="edmshrt_retriever",
    index_name="index-oai-edms-non-engg-standards",
    prompts={
        "instruction_prompt": (
            "EDMSHRT_INSTRUCTION_PROMPT",
            EDMSHRT_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "EDMSHRT_TOOL_DESCRIPTION_PROMPT",
            EDMSHRT_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config={
        "search": "query-to-be-replaced-by-retriever",
        "vectorQueries": [{"kind": "text", "k": 5, "fields": "chunk_vector"}],
        "filter": "prefix eq 'GHR'",
        "queryType": "semantic",
        "semanticConfiguration": "oai-semantic-config",
        "captions": "extractive",
        "answers": "extractive|count-3",
        "queryLanguage": "en-US",
        "top": 5,
    },
    citation_field_mappings={}
)

edmshrt_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
