from src.models import RetrieverToolSpec
from .prompts import (
    IPLMFAQ_INSTRUCTION_PROMPT,
    IPLMFAQ_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.core.tools.constants import SEARCH_CONFIG, CITATION_FIELD_MAPPINGS_ROW



tool_spec = RetrieverToolSpec(
    tool_name="iplmfaq_retriever",
    index_name= "index-oai-iplm-faq-alias",
    prompts={
        "instruction_prompt": (
            "IPLMFAQ_INSTRUCTION_PROMPT",
            IPLMFAQ_INSTRUCTION_PROMPT,
        ),  
        "tool_description_prompt": (
            "IPLMFAQ_TOOL_DESCRIPTION_PROMPT",
            IPLMFAQ_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config=SEARCH_CONFIG,
    citation_field_mappings=CITATION_FIELD_MAPPINGS_ROW
)

iplm_faq_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)