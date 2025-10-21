from src.models import RetrieverToolSpec
from .prompts import (
    FREMONTDEMO_INSTRUCTION_PROMPT,
    FREMONTDEMO_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.core.tools.constants import CITATION_FIELD_MAPPINGS_ROW

tool_spec = RetrieverToolSpec(
    tool_name="fremontdemo_retriever",
    index_name="index-oai-etch-alias",
    prompts={
        "instruction_prompt": (
            "FREMONTDEMO_INSTRUCTION_PROMPT",
            FREMONTDEMO_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "FREMONTDEMO_TOOL_DESCRIPTION_PROMPT",
            FREMONTDEMO_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config={
        "search": "query-to-be-replaced-by-retriever",
        "vectorQueries": [{"kind": "text", "k": 5, "fields": "chunk_vector"}],
        "filter": "directory eq 'Fremont_BiCS11_MH_Demo'",
        "queryType": "semantic",
        "semanticConfiguration": "oai-semantic-config",
        "captions": "extractive",
        "answers": "extractive|count-3",
        "queryLanguage": "en-US",
        "top": 5,
    },
    citation_field_mappings=CITATION_FIELD_MAPPINGS_ROW
)

fremontdemo_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
