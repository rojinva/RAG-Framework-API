from src.models import RetrieverToolSpec
from .prompts import EDMSENGSTANDARDS_INSTRUCTION_PROMPT, EDMSENGSTANDARDS_TOOL_DESCRIPTION_PROMPT
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.models.citation import CitationTagAliasSpec
from src.models.constants import FileExtension

tool_spec = RetrieverToolSpec(
    tool_name="edmsengstandards_retriever",
    index_name="index-oai-edms-engg-standards",
    prompts={
        "instruction_prompt": (
            "EDMSENGSTANDARDS_INSTRUCTION_PROMPT",
            EDMSENGSTANDARDS_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "EDMSENGSTANDARDS_TOOL_DESCRIPTION_PROMPT",
            EDMSENGSTANDARDS_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config={
        "search": "query-to-be-replaced-by-retriever",
        "vectorQueries": [{"kind": "text", "fields": "chunk_vector", "weight": 2}],
        "queryType": "semantic",
        "semanticConfiguration": "oai-semantic-config",
        "captions": "extractive",
        "answers": "extractive|count-3",
        "queryLanguage": "en-US",
        "top": 15,
    },
    citation_field_mappings={
        "row": CitationTagAliasSpec(
            default="ROW",
            file_extension_aliases={
                FileExtension.PPT: "Slide",
                FileExtension.PPTX: "Slide",
                FileExtension.PDF: "Page",
                FileExtension.XLS: "Row",
                FileExtension.XLSX: "Row",
                FileExtension.DOC: "Page",
                FileExtension.DOCX: "Page",
            },
        ),
        "sheet_name": CitationTagAliasSpec(
            default="SHEET NAME",
            file_extension_aliases={
                FileExtension.XLS: "Sheet",
                FileExtension.XLSX: "Sheet",
                FileExtension.DOC: "Info",
                FileExtension.DOCX: "Info",
            },
        ),
    },
)

edmsengstandards_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
