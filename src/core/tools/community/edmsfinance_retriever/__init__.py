from .retriever_tool import edmsfinance_retriever_tool
from src.core.tools.registry import register_tool

register_tool(edmsfinance_retriever_tool)