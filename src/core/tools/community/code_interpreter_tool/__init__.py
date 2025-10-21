from src.core.tools.registry import register_tool
from src.core.tools.community.code_interpreter_tool.tool import CodeInterpreterTool


code_interpreter = CodeInterpreterTool()
register_tool(code_interpreter)