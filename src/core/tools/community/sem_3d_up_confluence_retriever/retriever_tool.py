from src.models import RetrieverToolSpec
from .prompts import (
    SEM3DUPCONFLUENCE_INSTRUCTION_PROMPT,
    SEM3DUPCONFLUENCE_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool

tool_spec = RetrieverToolSpec(
    tool_name="sem_3d_up_confluence_retriever",
    index_name="index-oai-sem-3d-up-confluence",
    prompts={
        "instruction_prompt": (
            "SEM3DUPCONFLUENCE_INSTRUCTION_PROMPT",
            SEM3DUPCONFLUENCE_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "SEM3DUPCONFLUENCE_TOOL_DESCRIPTION_PROMPT",
            SEM3DUPCONFLUENCE_TOOL_DESCRIPTION_PROMPT,
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

sem3d_up_confluence_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
