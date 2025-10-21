from .retriever_tool import nsr_retriever_tool
from src.core.tools.registry import register_tool

register_tool(nsr_retriever_tool)