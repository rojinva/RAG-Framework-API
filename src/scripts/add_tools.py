from src.services.tools_db_service import mongo_client
from src.models.config import ToolConfig
from src.models import ToolType


def add_tool(args):

    tool_config = ToolConfig(
        name=args.get("name"),
        display_name=args.get("displayName"),
        description=args.get("description"),
        tool_type=ToolType.retriever_tool,
        security_group=args.get("securityGroup"),
    )

    return mongo_client.insert_document(tool_config.json())


if __name__ == "__main__":

    args = {
        "name": "",
        "displayName": "",
        "description": "",
        "tool_type": "",
        "security_group": "",
    }

    add_tool(args=args)
