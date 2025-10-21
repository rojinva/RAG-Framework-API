from .retriever_tool import confluence_retriever_tool
from src.core.tools.registry import register_tool

register_tool(confluence_retriever_tool)