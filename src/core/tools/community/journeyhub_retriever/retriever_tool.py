from src.models import RetrieverToolSpec
from .prompts import (
    JOURNEYHUB_INSTRUCTION_PROMPT,
    JOURNEYHUB_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.constants import SEARCH_CONFIG_NO_VECTOR_SEARCH
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.models.citation import CitationTagAliasSpec

tool_spec = RetrieverToolSpec(
    tool_name="journeyhub_retriever",
    index_name="index-oai-journeyhub-alias",
    prompts={
        "instruction_prompt": (
            "JOURNEYHUB_INSTRUCTION_PROMPT",
            JOURNEYHUB_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "JOURNEYHUB_TOOL_DESCRIPTION_PROMPT",
            JOURNEYHUB_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config=SEARCH_CONFIG_NO_VECTOR_SEARCH,
    citation_field_mappings= {
        "Training_ID": CitationTagAliasSpec(default="ID"),
        "Target_Audience": CitationTagAliasSpec(default="Target Audience")
    }
)

journeyhub_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
