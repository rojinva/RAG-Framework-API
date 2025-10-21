from .tool import user_scoped_sharepoint_tool
from src.core.tools.registry import register_tool

register_tool(user_scoped_sharepoint_tool)