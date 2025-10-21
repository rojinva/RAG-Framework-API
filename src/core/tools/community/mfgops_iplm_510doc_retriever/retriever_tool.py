from src.models import RetrieverToolSpec
from .prompts import (
    MFGOPSIPLM510_INSTRUCTION_PROMPT,
    MFGOPSIPLM510_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool

tool_spec = RetrieverToolSpec(
    tool_name="mfgops_iplm_510doc_retriever",
    index_name="index-oai-mfg-ops-iplm-510-docs",
    prompts={
        "instruction_prompt": (
            "MFGOPSIPLM510_INSTRUCTION_PROMPT",
            MFGOPSIPLM510_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "MFGOPSIPLM510_TOOL_DESCRIPTION_PROMPT",
            MFGOPSIPLM510_TOOL_DESCRIPTION_PROMPT,
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
    citation_field_mappings={}
)

mfgopsiplm510_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
