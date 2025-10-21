from src.models import RetrieverToolSpec, AccessControlParam, AccessControl
from src.core.tools.constants import CITATION_FIELD_MAPPINGS_ROW
from .prompts import (
    ETCH_INSTRUCTION_PROMPT,
    ETCH_REDACTED_INSTRUCTION_PROMPT,
    ETCH_TOOL_DESCRIPTION_PROMPT,
)
from .utils import get_accessible_sharepoint_site_names


tool_spec = RetrieverToolSpec(
    tool_name="etch_app_{application_name}_retriever",
    index_name="index-oai-etch-alias",
    prompts={
        "instruction_prompt": (
            "ETCH_INSTRUCTION_PROMPT",
            ETCH_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "ETCH_TOOL_DESCRIPTION_PROMPT",
            ETCH_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config={
        "search": "query-to-be-replaced-by-retriever",
        "vectorQueries": [{"kind": "text", "k": 5, "fields": "chunk_vector"}],
        "filter": "Application eq '{application_name_filter}'",
        "queryType": "semantic",
        "semanticConfiguration": "oai-semantic-config",
        "captions": "extractive",
        "answers": "extractive|count-3",
        "queryLanguage": "en-US",
        "top": 5,
    },
    citation_field_mappings=CITATION_FIELD_MAPPINGS_ROW,
    access_control=AccessControl(
        function=get_accessible_sharepoint_site_names,  # Function to determine accessible sharepoint site names
        param=AccessControlParam.ACCESS_TOKEN,  # Parameter type for the access control function
        filter_field="sharepoint_site_name",  # Field in the search service to be filtered
    ),
    additional_context={
        "parent_filename": "File Name",
        "source_file_created_by": "Author",
    },
)

redacted_tool_spec = RetrieverToolSpec(
    tool_name="etch_app_{application_name}_redacted_retriever",
    index_name="index-oai-etch-redacted-alias",
    prompts={
        "instruction_prompt": (
            "ETCH_REDACTED_INSTRUCTION_PROMPT",
            ETCH_REDACTED_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "ETCH_TOOL_DESCRIPTION_PROMPT",
            ETCH_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config={
        "search": "query-to-be-replaced-by-retriever",
        "vectorQueries": [{"kind": "text", "k": 5, "fields": "chunk_vector"}],
        "filter": "Application eq '{application_name_filter}'",
        "queryType": "semantic",
        "semanticConfiguration": "oai-semantic-config",
        "captions": "extractive",
        "answers": "extractive|count-3",
        "queryLanguage": "en-US",
        "top": 5,
    },
    citation_field_mappings=CITATION_FIELD_MAPPINGS_ROW,
    additional_context={
        "parent_filename": "File Name",
        "source_file_created_by": "Author",
    },
)