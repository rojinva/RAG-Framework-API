from src.models import RetrieverToolSpec
from .prompts import (
    SOFTWARE_RELEASE_NOTES_INSTRUCTION_PROMPT,
    SOFTWARE_RELEASE_NOTES_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool

tool_spec = RetrieverToolSpec(
    tool_name="softwarereleasenotes_retriever",
    index_name="index-oai-rpt-rng-alias",
    prompts={
        "instruction_prompt": (
            "SOFTWARE_RELEASE_NOTES_INSTRUCTION_PROMPT",
            SOFTWARE_RELEASE_NOTES_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "SOFTWARE_RELEASE_NOTES_TOOL_DESCRIPTION_PROMPT",
            SOFTWARE_RELEASE_NOTES_TOOL_DESCRIPTION_PROMPT,
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
    citation_field_mappings={},
)

software_release_notes_retriever_tool = LamBotRetrieverTool.from_tool_spec(
    tool_spec
)
