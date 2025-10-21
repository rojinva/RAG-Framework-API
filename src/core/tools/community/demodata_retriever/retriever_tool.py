from src.models import RetrieverToolSpec
from .prompts import (
    DEMODATA_INSTRUCTION_PROMPT,
    DEMODATA_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.core.tools.constants import SEARCH_CONFIG, CITATION_FIELD_MAPPINGS_ROW



tool_spec = RetrieverToolSpec(
    tool_name="demodata_retriever",
    index_name= "index-oai-demo-data-alias",
    prompts={
        "instruction_prompt": (
            "DEMODATA_INSTRUCTION_PROMPT",
            DEMODATA_INSTRUCTION_PROMPT,
        ),  
        "tool_description_prompt": (
            "DEMODATA_TOOL_DESCRIPTION_PROMPT",
            DEMODATA_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config=SEARCH_CONFIG,
    citation_field_mappings=CITATION_FIELD_MAPPINGS_ROW
)

demodata_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)