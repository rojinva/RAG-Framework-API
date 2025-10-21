from src.models import RetrieverToolSpec
from .prompts import (
    MFGOPSVFD_INSTRUCTION_PROMPT,
    MFGOPSVFD_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool

tool_spec = RetrieverToolSpec(
    tool_name="mfgopsvfd_retriever",
    index_name="index-oai-mfgops-vfd",
    prompts={
        "instruction_prompt": (
            "MFGOPSVFD_INSTRUCTION_PROMPT",
            MFGOPSVFD_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "MFGOPSVFD_TOOL_DESCRIPTION_PROMPT",
            MFGOPSVFD_TOOL_DESCRIPTION_PROMPT,
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

mfgopsvfd_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
