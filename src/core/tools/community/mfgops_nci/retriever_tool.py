from src.models import RetrieverToolSpec
from .prompts import (
    MFGOPSNCI_INSTRUCTION_PROMPT,
    MFGOPSNCI_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool

tool_spec = RetrieverToolSpec(
    tool_name= "mfgops_nci",
    index_name="index-oai-mfgops-nci",
    prompts={
        "instruction_prompt": (
            "MFGOPSNCI_INSTRUCTION_PROMPT",
             MFGOPSNCI_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "MFGOPSNCI_TOOL_DESCRIPTION_PROMPT,",
             MFGOPSNCI_TOOL_DESCRIPTION_PROMPT,
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

mfgopsnci_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
