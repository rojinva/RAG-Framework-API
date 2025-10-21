from src.models import RetrieverToolSpec
from .prompts import NCE_INSTRUCTION_PROMPT, NCE_TOOL_DESCRIPTION_PROMPT
from src.core.tools.common.retriever import LamBotRetrieverTool

tool_spec = RetrieverToolSpec(
    tool_name="nce_retriever",
    index_name="index-oai-nce-alias",
    prompts={
        "instruction_prompt": (
            "NCE_INSTRUCTION_PROMPT",
            NCE_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "NCE_TOOL_DESCRIPTION_PROMPT",
            NCE_TOOL_DESCRIPTION_PROMPT,
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

nce_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
