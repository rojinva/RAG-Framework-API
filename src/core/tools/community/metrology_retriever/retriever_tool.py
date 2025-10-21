from .prompts import METROLOGY_INSTRUCTION_PROMPT, METROLOGY_TOOL_DESCRIPTION_PROMPT
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.models.retriever_tool import RetrieverToolSpec
from src.core.tools.constants import SEARCH_CONFIG, CITATION_FIELD_MAPPINGS_ROW

tool_spec = RetrieverToolSpec(
    tool_name="metrology_retriever",
    index_name="index-oai-metrology-alias",
    prompts={
        "instruction_prompt": (
            "METROLOGY_INSTRUCTION_PROMPT",
            METROLOGY_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "METROLOGY_TOOL_DESCRIPTION_PROMPT",
            METROLOGY_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config=SEARCH_CONFIG,
    citation_field_mappings=CITATION_FIELD_MAPPINGS_ROW,
)

metrology_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
