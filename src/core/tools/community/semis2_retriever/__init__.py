from .retriever_tool import semis2_retriever_tool
from src.core.tools.registry import register_tool

register_tool(semis2_retriever_tool)