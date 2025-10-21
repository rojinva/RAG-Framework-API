from src.core.tools.community.fmea_conv.abstraction.fmea_agent_tool_spec_model import FMEAToolSpec, FMEARetrieverSpec
from .abstraction.fmea_agent_tool import LamBotFMEAAgentTool
from .prompts import (
    FMEA_AGENT_INSTRUCTION_PROMPT,
    FMEA_AGENT_ITEM_FUNCTION_PROMPT,
    FMEA_AGENT_POTENTIAL_FAILURE_MODE_PROMPT,
    FMEA_AGENT_POTENTIAL_CAUSE_OF_FAILURE_PROMPT,
    FMEA_AGENT_TOOL_DESCRIPTION_PROMPT
)

tool_spec = FMEAToolSpec(
    tool_name="fmea_creation_agent_tool",
    description="Tool for text to sql tasks",
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
    ),
    prompts={
        "instruction_prompt": (
            "FMEA_AGENT_INSTRUCTION_PROMPT",
            FMEA_AGENT_INSTRUCTION_PROMPT,
        ),
        "item_function_generation_prompt": (
            "FMEA_AGENT_ITEM_FUNCTION_PROMPT",
            FMEA_AGENT_ITEM_FUNCTION_PROMPT,
        ),
        "potential_failure_mode_prompt": (
            "FMEA_AGENT_POTENTIAL_FAILURE_MODE_PROMPT",
            FMEA_AGENT_POTENTIAL_FAILURE_MODE_PROMPT,
        ),
        "potential_cause_cause_of_failure_prompt": (
            "FMEA_AGENT_POTENTIAL_CAUSE_OF_FAILURE_PROMPT",
            FMEA_AGENT_POTENTIAL_CAUSE_OF_FAILURE_PROMPT,
        ),
            "tool_description_prompt": (
            "FMEA_TOOL_DESCRIPTION_PROMPT",
            FMEA_AGENT_TOOL_DESCRIPTION_PROMPT,
        ),
    },
)

fmea_agent_retriever_tool = LamBotFMEAAgentTool.from_tool_spec(tool_spec)
