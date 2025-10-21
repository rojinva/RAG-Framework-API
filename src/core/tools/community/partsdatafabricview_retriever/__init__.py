from src.core.tools.community.parts_view_retriever.retriever_tool import tool_spec
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.core.tools.registry import register_tool
import copy

tool_spec = copy.deepcopy(tool_spec)
tool_spec.tool_name = "partsdatafabricview_retriever"
tool_spec.index_name = "index-oai-parts-data-fabric-view-alias"

partsdatafabricview_retriever_tool = LamBotRetrieverTool.from_tool_spec(
    tool_spec
)

register_tool(partsdatafabricview_retriever_tool)