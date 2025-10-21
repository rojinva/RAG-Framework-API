from src.models import RetrieverToolSpec
from .prompts import (
    DESIGN_REVIEW_ATTACHMENTS_INSTRUCTION_PROMPT,
    DESIGN_REVIEW_ATTACHMENTS_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.models.citation import CitationTagAliasSpec

tool_spec = RetrieverToolSpec(
    tool_name="designreviewattachments_retriever",
    index_name="index-oai-designreview-attachments-alias",
    prompts={
        "instruction_prompt": (
            "DESIGN_REVIEW_ATTACHMENTS_INSTRUCTION_PROMPT",
            DESIGN_REVIEW_ATTACHMENTS_INSTRUCTION_PROMPT,
        ),  
        "tool_description_prompt": (
            "DESIGN_REVIEW_ATTACHMENTS_TOOL_DESCRIPTION_PROMPT",
            DESIGN_REVIEW_ATTACHMENTS_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config={
        "search": "query-to-be-replaced-by-retriever",
        "vectorQueries": [{"kind": "text", "k": 5, "fields": "chunk_vector"}],
        "queryType": "semantic",
        "semanticConfiguration": "oai-semantic-config",
        "captions": "extractive",
        "answers": "extractive|count-3",
        "queryLanguage": "en-US",
        "top": 5,
    },
    citation_field_mappings= {
        "row": CitationTagAliasSpec(default="ROW"),
        "sheet_name": CitationTagAliasSpec(default="Section"),
        "part_name": CitationTagAliasSpec(default="DR")
    }
)

design_review_attachments_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)