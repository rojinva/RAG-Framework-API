from .retriever_tool import swc_retriever_tool
from src.core.tools.registry import register_tool

register_tool(swc_retriever_tool)