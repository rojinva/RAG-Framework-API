from .retriever_tool import etch_retriever_tool
from src.core.tools.registry import register_tool

register_tool(etch_retriever_tool)