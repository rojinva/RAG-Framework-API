from src.models import RetrieverToolSpec
from .prompts import EDMSFINANCE_INSTRUCTION_PROMPT, EDMSFINANCE_TOOL_DESCRIPTION_PROMPT
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.models.citation import CitationTagAliasSpec
from src.models.constants import FileExtension

tool_spec = RetrieverToolSpec(
    tool_name="edmsfinance_retriever",
    index_name="index-oai-edms-non-engg-standards",
    prompts={
        "instruction_prompt": (
            "EDMSFINANCE_INSTRUCTION_PROMPT",
            EDMSFINANCE_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "EDMSFINANCE_TOOL_DESCRIPTION_PROMPT",
            EDMSFINANCE_TOOL_DESCRIPTION_PROMPT,
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
        "top": 15,
        "filter": "prefix eq 'FIN'"
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

edmsfinance_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
