from src.models import RetrieverToolSpec
from .prompts import (
    MATERIALDRAWING_INSTRUCTION_PROMPT,
    MATERIALDRAWING_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.models.citation import CitationTagAliasSpec


tool_spec = RetrieverToolSpec(
    tool_name="materialdrawing_retriever",
    index_name="index-oai-material-drawing-table-alias",
    prompts={
        "instruction_prompt": (
            "MATERIALDRAWING_INSTRUCTION_PROMPT",
            MATERIALDRAWING_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "MATERIALDRAWING_TOOL_DESCRIPTION_PROMPT",
            MATERIALDRAWING_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config={
        "search": "query-to-be-replaced-by-retriever",
        "queryType": "semantic",
        "semanticConfiguration": "oai-semantic-config",
        "captions": "extractive",
        "answers": "extractive|count-3",
        "queryLanguage": "en-US",
        "top": 5,
    },
    citation_field_mappings={
        "FileName": CitationTagAliasSpec(default="File"),
        "Revision": CitationTagAliasSpec(default="Revision")
    }
)

materialdrawing_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
