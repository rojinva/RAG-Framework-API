from src.models import RetrieverToolSpec
from .prompts import (
    WBT_COURSE_DESCRIPTION_INSTRUCTION_PROMPT,
    WBT_COURSE_DESCRIPTION_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool

tool_spec = RetrieverToolSpec(
    tool_name="wbt_course_description_retriever",
    index_name="index-oai-wbt-course-description",
    prompts={
        "instruction_prompt": (
            "WBT_COURSE_DESCRIPTION_INSTRUCTION_PROMPT",
            WBT_COURSE_DESCRIPTION_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "WBT_COURSE_DESCRIPTION_TOOL_DESCRIPTION_PROMPT",
            WBT_COURSE_DESCRIPTION_TOOL_DESCRIPTION_PROMPT,
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
    citation_field_mappings={},
)

wbt_course_description_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
