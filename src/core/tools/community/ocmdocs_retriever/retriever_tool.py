from src.models import RetrieverToolSpec
from .prompts import (
    OCM_CHATBOT_INSTRUCTION_PROMPT,
    OCM_CHATBOT_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool

tool_spec = RetrieverToolSpec(
    tool_name="ocmdocs_retriever",
    index_name="index-oai-dt-ocm",
    prompts={
        "instruction_prompt": (
            "OCM_CHATBOT_INSTRUCTION_PROMPT",
            OCM_CHATBOT_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "OCM_CHATBOT_TOOL_DESCRIPTION_PROMPT",
            OCM_CHATBOT_TOOL_DESCRIPTION_PROMPT,
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

ocm_retriver_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
