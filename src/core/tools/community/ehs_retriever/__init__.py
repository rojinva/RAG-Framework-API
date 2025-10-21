from .retriever_tool import ehs_retriever_tool
from src.core.tools.registry import register_tool

register_tool(ehs_retriever_tool)