from .retriever_tool import fremontdemo_retriever_tool
from src.core.tools.registry import register_tool

register_tool(fremontdemo_retriever_tool)