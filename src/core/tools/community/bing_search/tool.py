from typing import Type
from pydantic import BaseModel
from src.core.base import LamBotTool
from src.models.constants import ToolType
from src.models.web_search_tool import SearchInput
from langchain_community.tools.bing_search.tool import BingSearchRun


class LamBotBingSearchTool(LamBotTool, BingSearchRun):
    """LamBot Bing Search Tool that includes tool_type"""

    args_schema: Type[BaseModel] = SearchInput
    tool_type: ToolType = ToolType.non_retriever_tool
    description: str = (
        "A tool that searches the web for a given user query. Useful for when you need to answer questions about current events."
    )

    def __init__(self, **kwargs):
        BingSearchRun.__init__(self, **kwargs)
