from .retriever_tool import demodata_retriever_tool
from src.core.tools.registry import register_tool

register_tool(demodata_retriever_tool)