from .tool import hrt_text_to_sql_retriever_tool
from src.core.tools.registry import register_tool

register_tool(hrt_text_to_sql_retriever_tool)