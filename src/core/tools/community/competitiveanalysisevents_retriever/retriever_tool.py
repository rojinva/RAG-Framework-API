from src.models import RetrieverToolSpec
from .prompts import (
    COMPETITIVEANALYSISEVENTS_INSTRUCTION_PROMPT,
    COMPETITIVEANALYSISEVENTS_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.core.tools.constants import CITATION_FIELD_MAPPINGS_ROW

tool_spec = RetrieverToolSpec(
    tool_name="competitiveanalysisevents_retriever",
    index_name="index-oai-cfpa-alias",
    prompts={
        "instruction_prompt": (
            "COMPETITIVEANALYSISEVENTS_INSTRUCTION_PROMPT",
            COMPETITIVEANALYSISEVENTS_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "COMPETITIVEANALYSISEVENTS_TOOL_DESCRIPTION_PROMPT",
            COMPETITIVEANALYSISEVENTS_TOOL_DESCRIPTION_PROMPT,
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
        "filter": "sheet_name eq 'Competitive Analysis Events'"
    },
    citation_field_mappings=CITATION_FIELD_MAPPINGS_ROW
)

competitiveanalysisevents_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
