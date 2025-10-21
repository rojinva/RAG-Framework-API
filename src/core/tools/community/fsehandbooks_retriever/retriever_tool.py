from src.models import RetrieverToolSpec
from .prompts import (
    FSE_HANDBOOKS_INSTRUCTION_PROMPT,
    FSE_HANDBOOKS_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool

tool_spec = RetrieverToolSpec(
    tool_name="fsehandbooks_retriever",
    index_name="index-oai-wafer-alias",
    prompts={
        "instruction_prompt": (
            "FSE_HANDBOOKS_INSTRUCTION_PROMPT",
            FSE_HANDBOOKS_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "FSE_HANDBOOKS_TOOL_DESCRIPTION_PROMPT",
            FSE_HANDBOOKS_TOOL_DESCRIPTION_PROMPT,
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
    citation_field_mappings={},
)

fse_handbooks_retriever_tool = LamBotRetrieverTool.from_tool_spec(
    tool_spec
)
