from .retriever_tool import iplm_retriever_tool
from src.core.tools.registry import register_tool

register_tool(iplm_retriever_tool)