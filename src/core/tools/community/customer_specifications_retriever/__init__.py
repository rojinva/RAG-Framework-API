from .retriever_tool import customerspec_retriever_tool
from src.core.tools.registry import register_tool

register_tool(customerspec_retriever_tool)
