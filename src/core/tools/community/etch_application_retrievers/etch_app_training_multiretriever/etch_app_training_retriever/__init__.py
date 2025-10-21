from copy import deepcopy

from src.core.tools.registry import register_tool
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.core.tools.community.etch_application_retrievers.tool_spec import tool_spec


tool_spec = deepcopy(tool_spec)
tool_spec.tool_name = "etch_app_training_retriever"
tool_spec.search_config["filter"] = "Application eq 'Training'"

etch_app_training_retriever_tool = LamBotRetrieverTool.from_tool_spec(tool_spec)
register_tool(etch_app_training_retriever_tool)