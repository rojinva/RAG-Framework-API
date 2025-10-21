from src.models import RetrieverToolSpec, AccessControlParam, AccessControl
from .prompts import (
    ETCH_SHAREPOINT_SG_INSTRUCTION_PROMPT,
    ETCH_SHAREPOINT_SG_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.core.tools.constants import SEARCH_CONFIG, CITATION_FIELD_MAPPINGS_ROW
from src.core.tools.community.etch_sharepoint_sg_retriever.utils import get_accessible_sharepoint_site_names

tool_spec = RetrieverToolSpec(
    tool_name="etch_sharepoint_sg_retriever",
    index_name="index-oai-etch-alias",
    prompts={
        "instruction_prompt": (
            "ETCH_SHAREPOINT_SG_INSTRUCTION_PROMPT",
            ETCH_SHAREPOINT_SG_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "ETCH_SHAREPOINT_SG_TOOL_DESCRIPTION_PROMPT",
            ETCH_SHAREPOINT_SG_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config=SEARCH_CONFIG,
    citation_field_mappings=CITATION_FIELD_MAPPINGS_ROW,
    access_control=AccessControl(
        function=get_accessible_sharepoint_site_names,  # Function to determine accessible sharepoint site names
        param=AccessControlParam.ACCESS_TOKEN,  # Parameter type for the access control function
        filter_field="sharepoint_site_name",  # Field in the search service to be filtered
    )
)

etch_sharepoint_sg_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
