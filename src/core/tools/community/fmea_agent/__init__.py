from .tool import fmea_agent_retriever_tool
from src.core.tools.registry import register_tool

register_tool(fmea_agent_retriever_tool)