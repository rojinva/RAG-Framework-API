from src.core.tools.registry import register_tool
from src.core.tools.community.fishbone_diagram_tool.tool import FishboneDiagramTool

fishbone_diagram_tool = FishboneDiagramTool()
register_tool(fishbone_diagram_tool)
