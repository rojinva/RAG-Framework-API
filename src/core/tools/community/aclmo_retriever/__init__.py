from .retriever_tool import aclmo_retriever_tool
from src.core.tools.registry import register_tool

register_tool(aclmo_retriever_tool)