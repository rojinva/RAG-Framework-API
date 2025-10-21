from .tool import custom_sharepoint_tool
from src.core.tools.registry import register_tool

register_tool(custom_sharepoint_tool)