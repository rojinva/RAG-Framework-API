from src.core.tools.community.metadata_based_text_to_sql.abstraction.text_to_sql_tool_spec_model import TextToSQLToolSpec, TextToSQLRetrieverSpec
from src.core.tools.community.metadata_based_text_to_sql.abstraction.texttosql_tool import LamBotTextToSQLTool
from src.core.tools.community.metadata_based_text_to_sql.prompts import (
    TEXT_TO_SQL_INSTRUCTION_PROMPT,
    TEXT_TO_SQL_TOOL_DESCRIPTION_PROMPT,
    TEXT_TO_SQL_QUERY_GENERATION_PROMPT,
)

EXTRACTIVE_COUNT = "extractive|count-3"

tool_spec = TextToSQLToolSpec(
    tool_name="hrt_text_to_sql_tool",
    description="Tool for text to sql tasks",
    schema_retriever_spec=TextToSQLRetrieverSpec(
        index_name="index-oai-hrtext2sqlddl",
        search_config={
            "search": "query-to-be-replaced-by-retriever",
            "vectorQueries": [{"kind": "text", "k": 9, "fields": "chunk_vector"}],
            "queryType": "semantic",
            "semanticConfiguration": "oai-semantic-config",
            "captions": "extractive",
            "answers": EXTRACTIVE_COUNT,
            "queryLanguage": "en-US",
            "top": 5,
        },
    ),
    metadata_retriever_spec=TextToSQLRetrieverSpec(
        index_name="index-oai-hrtext2sqlmetadata",
        search_config={
            "search": "query-to-be-replaced-by-retriever",
            "vectorQueries": [{"kind": "text", "k": 9, "fields": "chunk_vector"}],
            "queryType": "semantic",
            "semanticConfiguration": "oai-semantic-config",
            "captions": "extractive",
            "answers": EXTRACTIVE_COUNT,
            "queryLanguage": "en-US",
            "top": 5,
        },
    ),
    sample_queries_retriever_spec=TextToSQLRetrieverSpec(
        index_name="index-oai-hrtext2sqlsamplequeries",
        search_config={
            "search": "query-to-be-replaced-by-retriever",
            "vectorQueries": [{"kind": "text", "k": 9, "fields": "chunk_vector"}],
            "queryType": "semantic",
            "semanticConfiguration": "oai-semantic-config",
            "captions": "extractive",
            "answers": EXTRACTIVE_COUNT,
            "queryLanguage": "en-US",
            "top": 5,
        },
    ),
    prompts={
        "instruction_prompt": (
            "TEXT_TO_SQL_INSTRUCTION_PROMPT",
            TEXT_TO_SQL_INSTRUCTION_PROMPT,
        ),
        "query_generation_prompt": (
            "TEXT_TO_SQL_QUERY_GENERATION_PROMPT",
            TEXT_TO_SQL_QUERY_GENERATION_PROMPT,
        ),
        "tool_description_prompt": (
            "TEXT_TO_SQL_TOOL_DESCRIPTION_PROMPT",
            TEXT_TO_SQL_TOOL_DESCRIPTION_PROMPT,
        ),
    },
)

hrt_text_to_sql_retriever_tool = LamBotTextToSQLTool.from_tool_spec(tool_spec)
