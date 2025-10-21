from src.models.citation import CitationTagAliasSpec
from src.models.constants import FileExtension

SEARCH_CONFIG = {
    "search": "query-to-be-replaced-by-retriever",
    "vectorQueries": [{"kind": "text", "k": 5, "fields": "chunk_vector"}],
    "queryType": "semantic",
    "semanticConfiguration": "oai-semantic-config",
    "captions": "extractive",
    "answers": "extractive|count-3",
    "queryLanguage": "en-US",
    "top": 5,
}

SEARCH_CONFIG_NO_VECTOR_SEARCH = {
    "search": "query-to-be-replaced-by-retriever",
    "queryType": "semantic",
    "semanticConfiguration": "oai-semantic-config",
    "captions": "extractive",
    "answers": "extractive|count-3",
    "queryLanguage": "en-US",
    "top": 5,
}

CITATION_FIELD_MAPPINGS = {
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
}

CITATION_FIELD_MAPPINGS_ROW = {
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
    )
}
