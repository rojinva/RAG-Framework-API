from src.models import RetrieverToolSpec
from .prompts import (
    SWC_INSTRUCTION_PROMPT,
    SWC_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool

tool_spec = RetrieverToolSpec(
    tool_name="swc_retriever",
    index_name="index-oai-swc-poc",
    prompts={
        "instruction_prompt": (
            "SWC_INSTRUCTION_PROMPT",
            SWC_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "SWC_TOOL_DESCRIPTION_PROMPT",
            SWC_TOOL_DESCRIPTION_PROMPT,
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

swc_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
