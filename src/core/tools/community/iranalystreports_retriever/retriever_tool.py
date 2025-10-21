from src.models import RetrieverToolSpec
from .prompts import (
    IRANALYST_REPORTS_INSTRUCTION_PROMPT,
    IRANALYST_REPORTS_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.models.citation import CitationTagAliasSpec

tool_spec = RetrieverToolSpec(
    tool_name="iranalystreports_retriever",
    index_name="index-oai-cfpa-alias",
    prompts={
        "instruction_prompt": (
            "IRANALYST_REPORTS_INSTRUCTION_PROMPT",
            IRANALYST_REPORTS_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "IRANALYST_REPORTS_TOOL_DESCRIPTION_PROMPT",
            IRANALYST_REPORTS_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    redact_pii=False,
    search_config={
        "search": "query-to-be-replaced-by-retriever",
        "vectorQueries": [{"kind": "text", "k": 5, "fields": "chunk_vector"}],
        "queryType": "semantic",
        "semanticConfiguration": "oai-semantic-config",
        "captions": "extractive",
        "answers": "extractive|count-3",
        "queryLanguage": "en-US",
        "top": 5,
        "filter": "sheet_name eq 'IR - Analyst Reports'"
    },
    citation_field_mappings={
        "row": CitationTagAliasSpec(default="Row"),
    }
)

iranalystreports_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
