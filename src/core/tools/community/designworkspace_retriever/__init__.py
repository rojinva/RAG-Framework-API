from .retriever_tool import designworkspace_retriever_tool
from src.core.tools.registry import register_tool

register_tool(designworkspace_retriever_tool)
