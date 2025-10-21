from .prompts import ETHICSCOMPLIANCE_INSTRUCTION_PROMPT, ETHICSCOMPLIANCE_TOOL_DESCRIPTION_PROMPT
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.models.retriever_tool import RetrieverToolSpec
from src.core.tools.constants import CITATION_FIELD_MAPPINGS_ROW

tool_spec = RetrieverToolSpec(
    tool_name="ethicscompliance_retriever",
    index_name="index-oai-ethics-compliance",
    prompts={
        "instruction_prompt": (
            "ETHICSCOMPLIANCE_INSTRUCTION_PROMPT",
            ETHICSCOMPLIANCE_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "ETHICSCOMPLIANCE_TOOL_DESCRIPTION_PROMPT",
            ETHICSCOMPLIANCE_TOOL_DESCRIPTION_PROMPT,
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
        "top": 5
    },
        citation_field_mappings=CITATION_FIELD_MAPPINGS_ROW

)

ethicscompliance_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
