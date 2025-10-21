from src.models import RetrieverToolSpec
from .prompts import (
    SERVICEDESKKB_INSTRUCTION_PROMPT,
    SERVICEDESKKB_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.models.citation import CitationTagAliasSpec
from src.models.constants import FileExtension

tool_spec = RetrieverToolSpec(
    tool_name="servicedeskkb_retriever",
    index_name="index-oai-servicedesk-kb",
    prompts={
        "instruction_prompt": (
            "SERVICEDESKKB_INSTRUCTION_PROMPT",
            SERVICEDESKKB_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "SERVICEDESKKB_TOOL_DESCRIPTION_PROMPT",
            SERVICEDESKKB_TOOL_DESCRIPTION_PROMPT,
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
    citation_field_mappings={
        "row": CitationTagAliasSpec(
            default="ROW",
            file_extension_aliases={
                FileExtension.XLS: "Row",
                FileExtension.XLSX: "Row",
                FileExtension.CSV: "Row",
                FileExtension.PDF: "Page",
            },
        ),
        "sheet_name": CitationTagAliasSpec(
            default="SHEET NAME",
            file_extension_aliases={
                FileExtension.XLS: "Sheet",
                FileExtension.XLSX: "Sheet",
            },
        ),
    },
)

servicedeskkb_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
