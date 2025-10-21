from src.models import RetrieverToolSpec
from .prompts import (
    IPLM_LLAMACLOUD_INSTRUCTION_PROMPT,
    IPLM_LLAMACLOUD_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.models.citation import CitationTagAliasSpec
from src.core.tools.constants import SEARCH_CONFIG


tool_spec = RetrieverToolSpec(
    tool_name="iplm_llamacloud_retriever",
    index_name="index-oai-iplm-samples-llamacloud-alias",
    prompts={
        "instruction_prompt": (
            "IPLM_LLAMACLOUD_INSTRUCTION_PROMPT",
            IPLM_LLAMACLOUD_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "IPLM_LLAMACLOUD_TOOL_DESCRIPTION_PROMPT",
            IPLM_LLAMACLOUD_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config=SEARCH_CONFIG,
    citation_field_mappings={
        "row": CitationTagAliasSpec(default="Page")
    }
)

iplm_llamacloud_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
