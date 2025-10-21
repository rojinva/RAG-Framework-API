from src.models import RetrieverToolSpec
from .prompts import (
    NSR_INSTRUCTION_PROMPT,
    NSR_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.constants import SEARCH_CONFIG_NO_VECTOR_SEARCH
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.models.citation import CitationTagAliasSpec


tool_spec = RetrieverToolSpec(
    tool_name="nsrstructured_retriever",
    index_name="index-oai-nsr-structured-alias",
    prompts={
        "instruction_prompt": (
            "NSR_INSTRUCTION_PROMPT",
            NSR_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "NSR_TOOL_DESCRIPTION_PROMPT",
            NSR_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config=SEARCH_CONFIG_NO_VECTOR_SEARCH,
    citation_field_mappings={
        "system_description": CitationTagAliasSpec(default="System"),
        "impacted_sub_system": CitationTagAliasSpec(default="Impacted Sub System")
    },
)

nsr_retriever_tool = LamBotRetrieverTool.from_tool_spec(
    tool_spec
)
