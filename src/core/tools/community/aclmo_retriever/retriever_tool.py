from src.models import RetrieverToolSpec
from .prompts import (
    ACLMO_INSTRUCTION_PROMPT,
    ACLMO_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.core.tools.constants import CITATION_FIELD_MAPPINGS_ROW

tool_spec = RetrieverToolSpec(
    tool_name="aclmo_retriever",
    index_name="index-oai-etch-alias",
    prompts={
        "instruction_prompt": (
            "ACLMO_INSTRUCTION_PROMPT",
            ACLMO_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "ACLMO_TOOL_DESCRIPTION_PROMPT",
            ACLMO_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config={
        "search": "query-to-be-replaced-by-retriever",
        "vectorQueries": [{"kind": "text", "k": 5, "fields": "chunk_vector"}],
        "filter": "directory eq 'ACL_MO_CnF'",
        "queryType": "semantic",
        "semanticConfiguration": "oai-semantic-config",
        "captions": "extractive",
        "answers": "extractive|count-3",
        "queryLanguage": "en-US",
        "top": 5,
    },
    citation_field_mappings=CITATION_FIELD_MAPPINGS_ROW
)

aclmo_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
