from src.core.tools.community.change_order_view_retriever.retriever_tool import tool_spec
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.core.tools.registry import register_tool
import copy

tool_spec = copy.deepcopy(tool_spec)
tool_spec.tool_name = "changenotificationsdatafabricview_retriever"
tool_spec.index_name = "index-oai-changenotifications-data-fabric-view-alias"

changenotificationsdatafabricview_retriever_tool = LamBotRetrieverTool.from_tool_spec(
    tool_spec
)

register_tool(changenotificationsdatafabricview_retriever_tool)