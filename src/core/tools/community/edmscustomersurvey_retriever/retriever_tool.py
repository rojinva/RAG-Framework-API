from src.models import RetrieverToolSpec
from .prompts import (
    EDMSCUSTOMERSURVEY_INSTRUCTION_PROMPT,
    EDMSCUSTOMERSURVEY_TOOL_DESCRIPTION_PROMPT,
)
from src.core.tools.common.retriever import LamBotRetrieverTool

tool_spec = RetrieverToolSpec(
    tool_name="edmscustomersurvey_retriever",
    index_name="index-oai-edms-engg-standards",
    prompts={
        "instruction_prompt": (
            "EDMSCUSTOMERSURVEY_INSTRUCTION_PROMPT",
            EDMSCUSTOMERSURVEY_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "EDMSCUSTOMERSURVEY_TOOL_DESCRIPTION_PROMPT",
            EDMSCUSTOMERSURVEY_TOOL_DESCRIPTION_PROMPT,
        ),
    },
    search_config={
        "search": "query-to-be-replaced-by-retriever",
        "vectorQueries": [{"kind": "text", "k": 5, "fields": "chunk_vector"}],
        "filter": "search.in(prefix, 'BOP, CAD, CCC, CCM, CCO, COE, CPL, CQA, CSBENG, EHS, FAC, FTD, GCS, GHR, GSP, IMS, INFOSEC, IST, LGL, MTL, OPC, OQA, PMP, POA, POP, PRP, SAF, SCV, SRM, STRMGMT, WAR')",
        "queryType": "semantic",
        "semanticConfiguration": "oai-semantic-config",
        "captions": "extractive",
        "answers": "extractive|count-3",
        "queryLanguage": "en-US",
        "top": 5,
    },
    citation_field_mappings={}
)

edmscustomersurvey_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
