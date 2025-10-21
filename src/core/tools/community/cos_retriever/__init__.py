from .retriever_tool import cos_retriever_tool
from src.core.tools.registry import register_tool

register_tool(cos_retriever_tool)