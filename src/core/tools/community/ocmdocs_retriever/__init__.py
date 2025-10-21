from .retriever_tool import ocm_retriver_tool
from src.core.tools.registry import register_tool

register_tool(ocm_retriver_tool)