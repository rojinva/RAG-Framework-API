from ..utils import get_asm_access_types
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.models.retriever_tool import AccessControlParam, AccessControl
from src.models import RetrieverToolSpec
from .prompts import (
    ESCALATIONSOLVER_CCI_INSTRUCTION_PROMPT,
    ESCALATIONSOLVER_CCI_TOOL_DESCRIPTION_PROMPT,
)

tool_spec = RetrieverToolSpec(
    tool_name="escalationsolver_cci_retriever",
    index_name="index-oai-escalationsolver-cci-alias",
    prompts={
        "instruction_prompt": (
            "ESCALATIONSOLVER_CCI_INSTRUCTION_PROMPT",
            ESCALATIONSOLVER_CCI_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "ESCALATIONSOLVER_CCI_TOOL_DESCRIPTION_PROMPT",
            ESCALATIONSOLVER_CCI_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config={
        "search": "query-to-be-replaced-by-retriever",
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

escalationsolver_cci_retriever_tool = LamBotRetrieverTool.from_tool_spec(
    tool_spec
)
