from .retriever_tool import fmea_retriever_tool
from src.core.tools.registry import register_tool

register_tool(fmea_retriever_tool)