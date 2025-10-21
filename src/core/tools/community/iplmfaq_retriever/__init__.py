from .retriever_tool import iplm_faq_retriever_tool
from src.core.tools.registry import register_tool

register_tool(iplm_faq_retriever_tool)