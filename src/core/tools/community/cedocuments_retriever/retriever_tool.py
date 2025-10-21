from src.models import RetrieverToolSpec
from src.core.tools.community.cedocuments_retriever.prompts import (
    CEDOCUMENTS_INSTRUCTION_PROMPT,
    CEDOCUMENTS_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.core.tools.constants import SEARCH_CONFIG, CITATION_FIELD_MAPPINGS_ROW


tool_spec = RetrieverToolSpec(
    tool_name="cedocuments_retriever",
    index_name="index-oai-ce-documents-alias",
    prompts={
        "instruction_prompt": (
            "CEDOCUMENTS_INSTRUCTION_PROMPT",
            CEDOCUMENTS_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "CEDOCUMENTS_TOOL_DESCRIPTION_PROMPT",
            CEDOCUMENTS_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config=SEARCH_CONFIG,
    citation_field_mappings=CITATION_FIELD_MAPPINGS_ROW,
)

ce_documents_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
