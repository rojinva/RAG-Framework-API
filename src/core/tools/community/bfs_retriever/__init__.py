from .retriever_tool import fast_retriever_tool
from src.core.tools.registry import register_tool

register_tool(fast_retriever_tool)