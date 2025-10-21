from .retriever_tool import fmea_chat_retriever_tool
from src.core.tools.registry import register_tool

register_tool(fmea_chat_retriever_tool)