from src.models import RetrieverToolSpec
from .prompts import (
    MEETINGMINER_INSTRUCTION_PROMPT,
    MEETINGMINER_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool

tool_spec = RetrieverToolSpec(
    tool_name="meetingminer_retriever",
    index_name="index-oai-meetingminer",
    prompts={
        "instruction_prompt": (
            "MEETINGMINER_INSTRUCTION_PROMPT",
            MEETINGMINER_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "MEETINGMINER_TOOL_DESCRIPTION_PROMPT",
            MEETINGMINER_TOOL_DESCRIPTION_PROMPT,
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

meetingminer_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
