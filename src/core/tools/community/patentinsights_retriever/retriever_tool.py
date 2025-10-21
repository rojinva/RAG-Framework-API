from .prompts import PATENTINSIGHTS_INSTRUCTION_PROMPT, PATENTINSIGHTS_TOOL_DESCRIPTION_PROMPT
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.models.retriever_tool import RetrieverToolSpec
from src.core.tools.constants import SEARCH_CONFIG, CITATION_FIELD_MAPPINGS_ROW

tool_spec = RetrieverToolSpec(
    tool_name="patentinsights_retriever",
    index_name="index-oai-patentinsights-alias",
    prompts={
        "instruction_prompt": (
            "PATENTINSIGHTS_INSTRUCTION_PROMPT",
            PATENTINSIGHTS_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "PATENTINSIGHTS_TOOL_DESCRIPTION_PROMPT",
            PATENTINSIGHTS_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config=SEARCH_CONFIG,
    citation_field_mappings=CITATION_FIELD_MAPPINGS_ROW,
)

patentinsights_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
