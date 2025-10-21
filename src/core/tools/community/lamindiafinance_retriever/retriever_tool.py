from src.models import RetrieverToolSpec
from .prompts import (
    LAMINDIAFINANCE_INSTRUCTION_PROMPT,
    LAMINDIAFINANCE_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.models.citation import CitationTagAliasSpec
from src.core.tools.constants import SEARCH_CONFIG


tool_spec = RetrieverToolSpec(
    tool_name="lamindiafinance_retriever",
    index_name="index-oai-lam-india-finance-alias",
    prompts={
        "instruction_prompt": (
            "LAMINDIAFINANCE_INSTRUCTION_PROMPT",
            LAMINDIAFINANCE_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "LAMINDIAFINANCE_TOOL_DESCRIPTION_PROMPT",
            LAMINDIAFINANCE_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config=SEARCH_CONFIG,
    citation_field_mappings={
        "row": CitationTagAliasSpec(default="Page")
    }
)

lamindiafinance_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
