from .prompts import WBT_CCI_INSTRUCTION_PROMPT, WBT_CCI_TOOL_DESCRIPTION_PROMPT
from ..utils import get_wbt_access_types
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.models import AccessControlParam, RetrieverToolSpec, AccessControl

tool_spec = RetrieverToolSpec(
    tool_name="wbt_cci_retriever",
    index_name="index-oai-wbt-cci-alias",
    prompts={
        "instruction_prompt": (
            "WBT_CCI_INSTRUCTION_PROMPT",
            WBT_CCI_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "WBT_CCI_TOOL_DESCRIPTION_PROMPT",
            WBT_CCI_TOOL_DESCRIPTION_PROMPT,
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
        function=get_wbt_access_types,  # The function to get access types
        param=AccessControlParam.USERNAME,  # The parameter type for the access control function
        filter_field="sheet_name",  # The field in the search service to be filtered
    )
)

wbt_cci_retriever_tool = LamBotRetrieverTool.from_tool_spec(
    tool_spec
)
