import os
from dotenv import load_dotenv

load_dotenv(override=True)

from langchain_community.utilities import BingSearchAPIWrapper
from .tool import LamBotBingSearchTool
from src.core.tools.registry import register_tool

NUM_RESULTS = 10

api_wrapper = BingSearchAPIWrapper(
    bing_search_url=os.getenv("BING_SEARCH_URL"),
    bing_subscription_key=os.getenv("BING_SUBSCRIPTION_KEY"),
    k=NUM_RESULTS,
)

bing_search_tool = LamBotBingSearchTool(
    name="bing_search", api_wrapper=api_wrapper, num_results=NUM_RESULTS
)
register_tool(bing_search_tool)
