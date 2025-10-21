from src.core.tools.community.fmea_conv.abstraction.fmea_agent_tool_spec_model import FMEAToolSpec, FMEARetrieverSpec
from .abstraction.fmea_conv_tool import LamBotFMEAConvTool
from .prompts import (
    FMEA_AGENT_INSTRUCTION_PROMPT,
    FMEA_AGENT_TOOL_DESCRIPTION_PROMPT
)

tool_spec = FMEAToolSpec(
    tool_name="fmea_conversational_agent_tool",
    description="Tool for fmea research and fmea generation tasks",
    historical_fmea_retriever_spec=FMEARetrieverSpec(
        index_name="index-oai-fmea-agent-042025-6",
        search_config={
            "search": "query-to-be-replaced-by-retriever",
            "queryType": "semantic",
            "semanticConfiguration": "oai-semantic-config",
            "captions": "extractive",
            "answers": "extractive|count-3",
            "queryLanguage": "en-US",
            "searchFields": "chunk",
            "top": 30,
        },
        citation_field_mappings={},
    ),
    escalation_solver_fmea_retriever_spec=FMEARetrieverSpec(
        index_name="index-oai-escalationsolver-052025-3",
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
    ),
    nce_fmea_retriever_spec=FMEARetrieverSpec(
        index_name="index-oai-nce-live-052025-2",
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
    ),
    prompts={
        "instruction_prompt": (
            "FMEA_AGENT_INSTRUCTION_PROMPT",
            FMEA_AGENT_INSTRUCTION_PROMPT,
        ),
            "tool_description_prompt": (
            "FMEA_TOOL_DESCRIPTION_PROMPT",
            FMEA_AGENT_TOOL_DESCRIPTION_PROMPT,
        ),
    },
)

fmea_conv_retriever_tool = LamBotFMEAConvTool.from_tool_spec(tool_spec)
