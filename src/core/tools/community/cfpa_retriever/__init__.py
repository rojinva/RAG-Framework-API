from .retriever_tool import cfpa_retriever_tool
from src.core.tools.registry import register_tool

register_tool(cfpa_retriever_tool)