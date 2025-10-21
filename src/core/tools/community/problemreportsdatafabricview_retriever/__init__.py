from src.core.tools.community.problem_reports_design_insights_retriever.retriever_tool import tool_spec
from src.core.tools.common.retriever import LamBotRetrieverTool
from src.core.tools.registry import register_tool
import copy

tool_spec = copy.deepcopy(tool_spec)
tool_spec.tool_name = "problemreportsdatafabricview_retriever"
tool_spec.index_name = "index-oai-problemreports-data-fabric-view-alias"

problemreportsdatafabricview_retriever_tool = LamBotRetrieverTool.from_tool_spec(
    tool_spec
)

register_tool(problemreportsdatafabricview_retriever_tool)