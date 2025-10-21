from copy import deepcopy

from src.core.tools.registry import register_tool
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.core.tools.community.etch_application_retrievers.tool_spec import (
    redacted_tool_spec,
)


tool_spec = deepcopy(redacted_tool_spec)
tool_spec.tool_name = "etch_app_pdr_redacted_retriever"
tool_spec.search_config["filter"] = "Application eq 'PDR'"

etch_app_pdr_redacted_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
register_tool(etch_app_pdr_redacted_retriever_tool)