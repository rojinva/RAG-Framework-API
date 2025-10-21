from src.models import RetrieverToolSpec
from .prompts import (
    CHANGEREQUESTS_INSTRUCTION_PROMPT,
    CHANGEREQUESTS_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.constants import SEARCH_CONFIG_NO_VECTOR_SEARCH
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.models.citation import CitationTagAliasSpec


tool_spec = RetrieverToolSpec(
    tool_name="changerequests_retriever",
    index_name="index-oai-change-requests-view-alias",
    prompts={
        "instruction_prompt": (
            "CHANGEREQUESTS_INSTRUCTION_PROMPT",
            CHANGEREQUESTS_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "CHANGEREQUESTS_TOOL_DESCRIPTION_PROMPT",
            CHANGEREQUESTS_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config=SEARCH_CONFIG_NO_VECTOR_SEARCH,
    citation_field_mappings={
        "revision": CitationTagAliasSpec(default="Revision")
    },
)

change_requests_retriever_tool = LamBotRetrieverTool.from_tool_spec(
    tool_spec
)
