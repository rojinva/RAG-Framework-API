from src.models import RetrieverToolSpec
from .prompts import (
    VIZGLOWUSERMANUAL_INSTRUCTION_PROMPT,
    VIZGLOWUSERMANUAL_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.core.tools.constants import SEARCH_CONFIG, CITATION_FIELD_MAPPINGS_ROW



tool_spec = RetrieverToolSpec(
    tool_name="vizglowusermanual_retriever",
    index_name= "index-oai-vizglow-alias",
    prompts={
        "instruction_prompt": (
            "VIZGLOWUSERMANUAL_INSTRUCTION_PROMPT",
            VIZGLOWUSERMANUAL_INSTRUCTION_PROMPT,
        ),  
        "tool_description_prompt": (
            "VIZGLOWUSERMANUAL_TOOL_DESCRIPTION_PROMPT",
            VIZGLOWUSERMANUAL_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config=SEARCH_CONFIG,
    citation_field_mappings=CITATION_FIELD_MAPPINGS_ROW
)

vizglowusermanual_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)