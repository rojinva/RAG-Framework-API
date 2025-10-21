from .prompts import DPGTRANSCRIPTS_INSTRUCTION_PROMPT, DPGTRANSCRIPTS_TOOL_DESCRIPTION_PROMPT
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.models.retriever_tool import RetrieverToolSpec
from src.core.tools.constants import SEARCH_CONFIG, CITATION_FIELD_MAPPINGS_ROW

tool_spec = RetrieverToolSpec(
    tool_name="dpgtranscripts_retriever",
    index_name="index-oai-dpg-transcripts-alias",
    prompts={
        "instruction_prompt": (
            "DPGTRANSCRIPTS_INSTRUCTION_PROMPT",
            DPGTRANSCRIPTS_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "DPGTRANSCRIPTS_TOOL_DESCRIPTION_PROMPT",
            DPGTRANSCRIPTS_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config=SEARCH_CONFIG,
    citation_field_mappings=CITATION_FIELD_MAPPINGS_ROW,
)

dpgtranscripts_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
