from typing import Dict
from langchain_core.tools import Tool

_tool_registry = {}

def register_tool(tool: Tool) -> None:
    """
    Registers a tool in the tool registry.

    Args:
        tool (Tool): The tool to be registered.

    Raises:
        ValueError: If the tool name is not found in tool_config and not provided, or if the tool is already registered.
    """

    tool_name = tool.name

    if tool_name in _tool_registry:
        raise ValueError(f"Tool {tool_name} is already registered")
    
    _tool_registry[tool_name] = tool

def get_tools() -> Dict[str, Tool]:
    """
    Retrieves all registered tools.

    Returns:
        Dict[str, Tool]: A dictionary of all registered tools with their names as keys.
    """
    return _tool_registry
    
def get_tool_by_name(tool_name: str) -> Tool:
    """
    Retrieves a tool by its name.

    Args:
        tool_name (str): The name of the tool to retrieve.

    Returns:
        Tool: The tool associated with the given name, or None if the tool is not found.
    """
    return _tool_registry.get(tool_name)