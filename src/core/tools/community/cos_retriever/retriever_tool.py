from .prompts import COS_INSTRUCTION_PROMPT, COS_TOOL_DESCRIPTION_PROMPT
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.models.retriever_tool import RetrieverToolSpec

tool_spec = RetrieverToolSpec(
    tool_name="cos_retriever",
    index_name="index-oai-cos-alias",
    prompts={
        "instruction_prompt": (
            "COS_INSTRUCTION_PROMPT",
            COS_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "COS_TOOL_DESCRIPTION_PROMPT",
            COS_TOOL_DESCRIPTION_PROMPT,
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

cos_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
