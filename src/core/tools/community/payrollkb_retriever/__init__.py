from .retriever_tool import payrollkb_retriever_tool
from src.core.tools.registry import register_tool

register_tool(payrollkb_retriever_tool)