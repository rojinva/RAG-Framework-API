from .retriever_tool import escalationsolver_retriever_tool
from src.core.tools.registry import register_tool

register_tool(escalationsolver_retriever_tool)
