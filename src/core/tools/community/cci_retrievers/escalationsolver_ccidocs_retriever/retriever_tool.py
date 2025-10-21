from .prompts import (
    ESCALATIONSOLVER_CCIDOCS_INSTRUCTION_PROMPT,
    ESCALATIONSOLVER_CCIDOCS_TOOL_DESCRIPTION_PROMPT,
)
from ..utils import get_asm_access_types
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.models import AccessControlParam, RetrieverToolSpec, AccessControl

tool_spec = RetrieverToolSpec(
    tool_name="escalationsolver_ccidocs_retriever",
    index_name="index-oai-escalationsolver-ccidocs",
    prompts={
        "instruction_prompt": (
            "ESCALATIONSOLVER_CCIDOCS_INSTRUCTION_PROMPT",
            ESCALATIONSOLVER_CCIDOCS_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "ESCALATIONSOLVER_CCIDOCS_TOOL_DESCRIPTION_PROMPT",
            ESCALATIONSOLVER_CCIDOCS_TOOL_DESCRIPTION_PROMPT,
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
    access_control=AccessControl(
        function=get_asm_access_types,  # The function to get access types
        param=AccessControlParam.USERNAME,  # The parameter type for the access control function
        filter_field="sheet_name",  # The field in the search service to be filtered
    )
)

escalationsolver_ccidocs_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)