from src.models import RetrieverToolSpec
from .prompts import (
    MFGOPSTEESCALATION_INSTRUCTION_PROMPT,
    MFGOPSTEESCALATION_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool

tool_spec = RetrieverToolSpec(
    tool_name="mfgopsteescalation_retriever",
    index_name="index-oai-mfgops-te-escalation",
    prompts={
        "instruction_prompt": (
            "MFGOPSTEESCALATION_INSTRUCTION_PROMPT",
            MFGOPSTEESCALATION_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "MFGOPSTEESCALATION_TOOL_DESCRIPTION_PROMPT",
            MFGOPSTEESCALATION_TOOL_DESCRIPTION_PROMPT,
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

mfgopsteescalation_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
