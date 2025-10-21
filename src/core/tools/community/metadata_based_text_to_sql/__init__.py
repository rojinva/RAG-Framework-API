from .tool import text_to_sql_retriever_tool
from src.core.tools.registry import register_tool

register_tool(text_to_sql_retriever_tool)