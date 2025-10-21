from typing import List
from pymongo.collection import Collection
from src.models.config import ToolConfig
from src.core.database.lambot_config import LamBotConfigDB
from src.core.utils.ms_graph_utils import has_copilot_access
from dotenv import load_dotenv

CUSTOM_SHAREPOINT_TOOL_NAME = "custom_sharepoint_tool"
USER_SCOPED_SHAREPOINT_TOOL_NAME = "user_scoped_sharepoint_tool"

load_dotenv()

class ToolConfigDB:
    def __init__(self, collection: Collection, lambot_config_db: LamBotConfigDB):
        self.collection = collection
        self.lambot_config_db = lambot_config_db

    def fetch_all_tools(self, user_role: str, security_group_list: List[str]) -> List[ToolConfig]:
        """
        Fetch all tool configurations and set the user_has_access field based on the user's role and security groups.

        Args:
            user_role (str): The role of the user (e.g., "admin", "user", "creator").
            security_group_list (List[str]): The list of security groups the user belongs to.

        Returns:
            List[ToolConfig]: A list of ToolConfig objects with the user_has_access field set accordingly.
        """
        tool_configs = []

        # Fetch all tools from the collection
        all_tools = list(self.collection.find())

        if user_role == "admin":
            # Admins have access to all tools
            for document in all_tools:
                document.pop("_id")
                document["user_has_access"] = True
                tool_configs.append(ToolConfig(**document))
        else:
            # For users and creators, determine access based on security groups
            for document in all_tools:
                document.pop("_id")
                # Check if the user's security groups cover all the tool's security group ids
                document["user_has_access"] = set(document["security_group_ids"]).issubset(security_group_list)

                if document["name"] in [CUSTOM_SHAREPOINT_TOOL_NAME, USER_SCOPED_SHAREPOINT_TOOL_NAME] and document["user_has_access"]:
                    document["user_has_access"] = has_copilot_access()
                tool_configs.append(ToolConfig(**document))

        return tool_configs

    def add_tool(self, tool_config: ToolConfig) -> ToolConfig:

        # Check if a tool with the same name or display name already exists
        existing_tool = self.collection.find_one({
            "$or": [
            {"name": tool_config.name},
            {"display_name": tool_config.display_name}
            ]
        })
        if existing_tool:
            raise ValueError("A tool with the same name or displayName already exists.")
        document = tool_config.model_dump()
        result = self.collection.insert_one(document)
        inserted_document = self.collection.find_one({"_id": result.inserted_id})
        inserted_document.pop("_id")
        return ToolConfig(**inserted_document)

    def fetch_tools(self, tool_names: List[str], user_role: str, security_group_list: List[str]) -> List[ToolConfig]:
        """
        Fetch ToolConfig objects from the toolConfigs collection based on tool names.

        Args:
            tool_names (List[str]): List of tool names to fetch.
            user_role (str): The role of the user (e.g., "admin", "user", "creator").
            security_group_list (List[str]): The list of security groups the user belongs to.

        Returns:
            List[ToolConfig]: List of ToolConfig objects.
        """
        tool_documents = self.collection.find({"name": {"$in": tool_names}})
        tool_configs = []

        if user_role == "admin":
            # Admins have access to all tools
            for document in tool_documents:
                document.pop("_id")
                document["user_has_access"] = True
                tool_configs.append(ToolConfig(**document))
        else:
            # For users and creators, determine access based on security groups
            for document in tool_documents:
                document.pop("_id")
                # Check if the user's security groups cover all the tool's security group ids
                document["user_has_access"] = set(document["security_group_ids"]).issubset(security_group_list)

                if document["name"] in [CUSTOM_SHAREPOINT_TOOL_NAME, USER_SCOPED_SHAREPOINT_TOOL_NAME] and document["user_has_access"]:
                    document["user_has_access"] = has_copilot_access()

                tool_configs.append(ToolConfig(**document))

        return tool_configs
    
    def fetch_tool(self, tool_name: str) -> ToolConfig:
        
        query = {"name": tool_name}

        document = self.collection.find_one(query)
        
        if not document:
            raise ValueError(f"No tool with the name {tool_name} could be found.")
        
        document.pop("_id", None)
        return ToolConfig(**document)
    
    def delete_tool(self, tool_name: str) -> bool:
        """
        Delete a tool from the toolConfigs collection.

        Args:
            tool_name (str): Name of the tool to delete.

        Returns:
            str: Name of the deleted tool.
        """

        # Check if the requested tool exists
        tool_exists = self.fetch_tool(tool_name=tool_name)
        if not tool_exists:
            raise ValueError("ToolConfig not found")
        
        tool_usage = self.lambot_config_db.check_tool_usage([tool_name])
        if tool_usage:
            raise ValueError(f"Deleting a tool config that is currently being used is forbidden. The following tool(s) are being used by the corresponding LamBot(s): {tool_usage}")
        
        is_deleted_result = self.collection.delete_one({"name": tool_name})
        
        if is_deleted_result.deleted_count > 0:
            return True
        else:
            return False
        
    def update_tool(self, tool_name: str, tool_config: ToolConfig) -> ToolConfig:
        """
        Updates the configuration of an existing tool.
        Args:
            tool_name (str): The name of the tool to update.
            tool_config (ToolConfig): The new configuration for the tool.
        Returns:
            ToolConfig: The updated tool configuration.
        Raises:
            ValueError: If the tool configuration is not found.
            ValueError: If the tool name is modified.
            ValueError: If a tool with the same display name already exists.
            ValueError: If no changes were made to the tool configuration.
        """
        
        # Get the tool to update
        old_tool_config = self.fetch_tool(tool_name=tool_name)
        if not old_tool_config:
            raise ValueError("ToolConfig not found")

        # Check that user has not attempted to modify the tool name
        if tool_name != tool_config.name:
            raise ValueError("Tool name cannot be modified.")
        
        # Check that the display name is unique
        existing_tool_display_name = self.collection.find_one({
            "display_name": tool_config.display_name,
            "name": {"$ne": tool_name}
        })
        if existing_tool_display_name:
            raise ValueError("A tool with the same display name already exists. Display names must be unique.")


        # Update the tool configuration
        ### Update this to support search by tool id for lambot-439 story
        update_result = self.collection.update_one(
            {"name": tool_name},
            {"$set": tool_config.model_dump()}
        )

        if update_result.modified_count == 0:
            raise ValueError("No changes were made to the tool configuration")

        updated_document = self.collection.find_one({"name": tool_name})
        updated_document.pop("_id")
        return ToolConfig(**updated_document)
    
    def check_tools_exist(self, tool_names: List[str]) -> bool:
        """
        Check if all tools in the list exist in the tool collection.

        Args:
            tool_names (List[str]): List of tool names to check.

        Returns:
            bool: True if all tools exist, False otherwise.
        """
        existing_tools = self.collection.find({"name": {"$in": tool_names}})
        existing_tool_names = {tool["name"] for tool in existing_tools}
        return set(tool_names).issubset(existing_tool_names)
