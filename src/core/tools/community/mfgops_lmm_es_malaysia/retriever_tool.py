from src.models import RetrieverToolSpec
from .prompts import (
    MFGOPSMALAYSIA_INSTRUCTION_PROMPT,
    MFGOPSMALAYSIA_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool

tool_spec = RetrieverToolSpec(
    tool_name="mfgops_lmm_es_malaysia",
    index_name="index-oai-mfgops-lmm-es-malasiya",
    prompts={
        "instruction_prompt": (
            "MFGOPSMALAYSIA_INSTRUCTION_PROMPT",
             MFGOPSMALAYSIA_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "MFGOPSMALAYSIA_TOOL_DESCRIPTION_PROMPT,",
             MFGOPSMALAYSIA_TOOL_DESCRIPTION_PROMPT,
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

mfgopsmalaysia_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
