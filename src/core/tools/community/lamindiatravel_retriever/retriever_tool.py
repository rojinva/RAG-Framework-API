from src.models import RetrieverToolSpec
from .prompts import (
    LAMINDIATRAVEL_INSTRUCTION_PROMPT,
    LAMINDIATRAVEL_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.models.citation import CitationTagAliasSpec
from src.core.tools.constants import SEARCH_CONFIG


tool_spec = RetrieverToolSpec(
    tool_name="lamindiatravel_retriever",
    index_name="index-oai-lam-travel-alias",
    prompts={
        "instruction_prompt": (
            "LAMINDIATRAVEL_INSTRUCTION_PROMPT",
            LAMINDIATRAVEL_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "LAMINDIATRAVEL_TOOL_DESCRIPTION_PROMPT",
            LAMINDIATRAVEL_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config=SEARCH_CONFIG,
    citation_field_mappings={
        "row": CitationTagAliasSpec(default="Page")
    }
)

lamindiatravel_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
