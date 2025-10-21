from .retriever_tool import journeyhub_retriever_tool
from src.core.tools.registry import register_tool

register_tool(journeyhub_retriever_tool)
