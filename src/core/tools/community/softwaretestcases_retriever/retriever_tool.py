from src.models import RetrieverToolSpec
from .prompts import (
    SOFTWARE_TEST_CASES_INSTRUCTION_PROMPT,
    SOFTWARE_TEST_CASES_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool

tool_spec = RetrieverToolSpec(
    tool_name="softwaretestcases_retriever",
    index_name="index-oai-rpt-track-alias",
    prompts={
        "instruction_prompt": (
            "SOFTWARE_TEST_CASES_INSTRUCTION_PROMPT",
            SOFTWARE_TEST_CASES_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "SOFTWARE_TEST_CASES_TOOL_DESCRIPTION_PROMPT",
            SOFTWARE_TEST_CASES_TOOL_DESCRIPTION_PROMPT,
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

software_test_cases_retriever_tool = LamBotRetrieverTool.from_tool_spec(
    tool_spec
)
