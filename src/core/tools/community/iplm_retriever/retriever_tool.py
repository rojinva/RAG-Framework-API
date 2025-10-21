from src.models import RetrieverToolSpec
from .prompts import IPLM_INSTRUCTION_PROMPT, IPLM_TOOL_DESCRIPTION_PROMPT
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.models.citation import CitationTagAliasSpec

tool_spec = RetrieverToolSpec(
    tool_name="iplm_retriever",
    index_name="index-oai-iplm-alias",
    prompts={
        "instruction_prompt": (
            "IPLM_INSTRUCTION_PROMPT",
            IPLM_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "IPLM_TOOL_DESCRIPTION_PROMPT",
            IPLM_TOOL_DESCRIPTION_PROMPT,
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
        "row": CitationTagAliasSpec(default="Page")
    }
)

iplm_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
