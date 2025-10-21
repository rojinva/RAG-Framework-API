from .retriever_tool import multimodal_retriever_tool
from src.core.tools.registry import register_tool

register_tool(multimodal_retriever_tool)