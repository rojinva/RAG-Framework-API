from src.models import RetrieverToolSpec
from .prompts import (
    SABRE3D_EPL_INSTRUCTION_PROMPT,
    SABRE3D_EPL_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.core.tools.constants import SEARCH_CONFIG, CITATION_FIELD_MAPPINGS_ROW


tool_spec = RetrieverToolSpec(
    tool_name="sabre3d_epl_retriever",
    index_name= "index-oai-sabre3d-epl-alias",
    prompts={
        "instruction_prompt": (
            "SABRE3D_EPL_INSTRUCTION_PROMPT",
            SABRE3D_EPL_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "SABRE3D_EPL_TOOL_DESCRIPTION_PROMPT",
            SABRE3D_EPL_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config=SEARCH_CONFIG,
    citation_field_mappings=CITATION_FIELD_MAPPINGS_ROW
)

sabre3d_epl_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)