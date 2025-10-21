from .prompts import TECHMEMO_INSTRUCTION_PROMPT, TECHMEMO_TOOL_DESCRIPTION_PROMPT
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.models.retriever_tool import RetrieverToolSpec

tool_spec = RetrieverToolSpec(
    tool_name="techmemo_retriever",
    index_name="index-oai-techmemo-alias",
    prompts={
        "instruction_prompt": (
            "TECHMEMO_INSTRUCTION_PROMPT",
            TECHMEMO_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "TECHMEMO_TOOL_DESCRIPTION_PROMPT",
            TECHMEMO_TOOL_DESCRIPTION_PROMPT,
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

techmemo_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
