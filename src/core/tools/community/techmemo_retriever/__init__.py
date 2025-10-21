from .retriever_tool import techmemo_retriever_tool
from src.core.tools.registry import register_tool

register_tool(techmemo_retriever_tool)
