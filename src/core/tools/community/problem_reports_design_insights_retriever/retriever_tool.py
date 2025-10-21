from src.models import RetrieverToolSpec
from .prompts import (
    PROBLEM_REPORTS_DESIGN_INSIGHTS_INSTRUCTION_PROMPT,
    PROBLEM_REPORTS_DESIGN_INSIGHTS_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool

tool_spec = RetrieverToolSpec(
    tool_name="problemreportsdesigninsights_retriever",
    index_name="index-oai-problemreports-alias",
    prompts={
        "instruction_prompt": (
            "PROBLEM_REPORTS_DESIGN_INSIGHTS_INSTRUCTION_PROMPT",
            PROBLEM_REPORTS_DESIGN_INSIGHTS_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "PROBLEM_REPORTS_DESIGN_INSIGHTS_TOOL_DESCRIPTION_PROMPT",
            PROBLEM_REPORTS_DESIGN_INSIGHTS_TOOL_DESCRIPTION_PROMPT,
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

problem_reports_design_insights_retriever_tool = LamBotRetrieverTool.from_tool_spec(
    tool_spec
)
