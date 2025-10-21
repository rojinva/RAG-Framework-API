from .retriever_tool import nce_retriever_tool
from src.core.tools.registry import register_tool

register_tool(nce_retriever_tool)