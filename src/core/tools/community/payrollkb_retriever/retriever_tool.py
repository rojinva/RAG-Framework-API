from src.models import RetrieverToolSpec
from .prompts import (
    PAYROLLKB_INSTRUCTION_PROMPT,
    PAYROLLKB_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.core.tools.constants import SEARCH_CONFIG, CITATION_FIELD_MAPPINGS

tool_spec = RetrieverToolSpec(
    tool_name="payrollkb_retriever",
    index_name="index-oai-payroll-kb",
    prompts={
        "instruction_prompt": (
            "PAYROLLKB_INSTRUCTION_PROMPT",
            PAYROLLKB_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "PAYROLLKB_TOOL_DESCRIPTION_PROMPT",
            PAYROLLKB_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config=SEARCH_CONFIG,
    citation_field_mappings=CITATION_FIELD_MAPPINGS
)

payrollkb_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
