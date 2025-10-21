from src.models import RetrieverToolSpec
from .prompts import (
    CUSTOMERSURVEY_INSTRUCTION_PROMPT,
    CUSTOMERSURVEY_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool

tool_spec = RetrieverToolSpec(
    tool_name="customersurvey_retriever",
    index_name="index-oai-customersurvey",
    prompts={
        "instruction_prompt": (
            "CUSTOMERSURVEY_INSTRUCTION_PROMPT",
            CUSTOMERSURVEY_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "CUSTOMERSURVEY_TOOL_DESCRIPTION_PROMPT",
            CUSTOMERSURVEY_TOOL_DESCRIPTION_PROMPT,
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

customersurvey_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
