from src.models.config import LamBotConfig, ToolConfig
from dotenv import load_dotenv
from uuid import uuid4, UUID
from typing import Optional, List, Dict, Any
import datetime
from collections import defaultdict
from pymongo.collection import Collection
from src.core.database.lambot_config_utils import package_lambot_config_with_tools
from src.core.utils.access_condition_helper import access_condition_checks
from src.models.constants import LamBotConfigAccessibiltiy
from src.core.context.vars import user_email_var
from src.core.common.exceptions import *

load_dotenv()
    
class LamBotConfigDB:

    def __init__(self, collection: Collection):
        """
        Initialize the LamBotConfigDB with a MongoDB collection.

        Args:
            collection (Collection): MongoDB collection instance to interact with the MongoDB collection.
        """
        self.collection = collection
    
    def _prepare_lambot_document(self, lambot_config: LamBotConfig) -> Dict[str, Any]:
        """
        Prepare the LamBot configuration MongoDB document for insertion or update.
        Checks if all tools exist in the ToolConfig collection and prepares the document accordingly.

        Args:
            lambot_config (LamBotConfig): LamBotConfig instance containing the configuration details.

        Returns:
            Dict[str, Any]: A dictionary containing the prepared document or an error message if tools are missing.
        """
        # Extract tool names for tools and selected_tools
        tool_names = [tool.name for tool in lambot_config.tools]
        selected_tool_names = [tool.name for tool in lambot_config.default_query_config.selected_tools]

        language_model_name = lambot_config.default_query_config.language_model.name
        supported_language_model_names = [llm.name for llm in lambot_config.supported_language_models]

        # Check if all tools exist in the ToolConfig collection
        all_tool_names = set(tool_names + selected_tool_names)
        if not self.tool_config_service.check_tools_exist(list(all_tool_names)):
            missing_tools = all_tool_names - set(tool.name for tool in self.tool_config_service.fetch_tools(list(all_tool_names)))
            return {"error": f"Missing tool configs for: {', '.join(missing_tools)}"}

        # Prepare the document for insertion or update
        document = lambot_config.model_dump()
        document["tools"] = tool_names
        document["default_query_config"]["selected_tools"] = selected_tool_names

        document["default_query_config"]["language_model"] = language_model_name
        document["supported_language_models"] = supported_language_model_names

        # Convert AnyUrl objects to strings for MongoDB compatibility
        if lambot_config.sharepoint_urls:
            document["sharepoint_urls"] = [str(url) for url in lambot_config.sharepoint_urls]

        return {"document": document}

    def add_lambot(self, lambot_config: LamBotConfig) -> Dict[str, Any]:
        """
        Add a new LamBot configuration to the MongoDB collection.
        When writing to MongoDB, only tool names are written, not the entire tool config.

        Args:
            lambot_config (LamBotConfig): LamBotConfig instance containing the configuration details.

        Returns:
            Dict[str, Any]: A dictionary containing a success message and the inserted document ID, or an error message.
        """
        # Validate the lambot config using the validator
        validation_result = self.validator.validate_for_write(lambot_config)
        
        if not validation_result["valid"]:
            return {"message": validation_result["message"]}
        
        # check if the name is already in use
        existing_lambot = self.collection.find_one({"name": lambot_config.name})
        if existing_lambot:
            raise AlreadyExistsError(
                f"LamBot configuration with name '{lambot_config.name}' already exists."
            )
        

        # Auto-populate fields
        lambot_config.id = str(uuid4())
        lambot_config.creator = user_email_var.get("email").lower()
        lambot_config.creation_date = str(datetime.datetime.now())
        lambot_config.last_modified_date = lambot_config.creation_date

        # Prepare the document
        result = self._prepare_lambot_document(lambot_config)
        if "error" in result:
            return {"message": f"Failed to insert LamBot configuration. {result['error']}"}

        # Write the MongoDB document
        inserted_document = self.collection.insert_one(result["document"])
        
        if inserted_document.inserted_id:
            return {
                "message": "LamBot configuration successfully inserted.",
                "id": lambot_config.id,
                "name": lambot_config.name
            }
        else:
            return {"message": "Failed to insert LamBot configuration."}

    def update_lambot(self, lambot_id: UUID, lambot_config: LamBotConfig, tool_configs_list: List[ToolConfig]) -> LamBotConfig:
        """
        Update an existing LamBot configuration in the MongoDB collection.
        When writing to MongoDB, only tool names are written, not the entire tool config.

        Args:
            lambot_id (UUID): UUID of the LamBot configuration to update.
            lambot_config (LamBotConfig): LamBotConfig instance containing the updated configuration details.
            tool_configs_list (List[ToolConfig]): List of ToolConfig instances representing the tools the user has access to.

        Returns:
            LamBotConfig: The updated LamBot configuration.
        """
        # Get the LamBot to update (needed to preserve fields like id)
        old_lambot_config = self.collection.find_one({"id": str(lambot_id)})

        # raise Exception if not found
        if not old_lambot_config:
            raise NotFoundError("LamBot configuration not found.")

        # Preserve and update values not editable by the client
        lambot_config.id = old_lambot_config["id"]  # Preserve the old id
        lambot_config.creator = old_lambot_config["creator"]  # Preserve the old creator
        lambot_config.creation_date = old_lambot_config["creation_date"]  # Preserve the old creation_date
        lambot_config.last_modified_date = datetime.datetime.now()  # Update the last_modified_date

        # Prepare the document
        result = self._prepare_lambot_document(lambot_config)
        if "error" in result:
            raise ValueError(f"Failed to prepare LamBot document. {result['error']}")

        # Update the collection
        update_result = self.collection.update_one({"id": str(lambot_id)}, {"$set": result["document"]})

        if update_result.modified_count > 0:
            # Fetch the updated document from the database to ensure consistency
            updated_document = self.collection.find_one({"id": str(lambot_id)})
            if updated_document:
                updated_document.pop("_id", None)
                language_model_configs_list = self.language_model_config_service.fetch_all_language_models()
                return package_lambot_config_with_tools(updated_document, tool_configs_list, language_model_configs_list)
            else:
                raise RuntimeError("Failed to retrieve updated LamBot configuration.")
        else:
            raise RuntimeError("Failed to update LamBot configuration.")

    def transfer_lambot_ownership(self, lambot_id: UUID, new_owner_email: str) -> Dict[str, str]:
        """
        Transfer ownership of a LamBot configuration to a new owner.
        Only updates the owner field without affecting other configuration.

        Args:
            lambot_id (UUID): UUID of the LamBot configuration to transfer.
            new_owner_email (str): Email address of the new owner.

        Returns:
            Dict[str, str]: A dictionary containing the new owner information.
        """
        # Check if the LamBot exists
        old_lambot_config = self.collection.find_one({"id": str(lambot_id)})
        
        if not old_lambot_config:
            raise NotFoundError("LamBot configuration not found.")

        # Update only the owner field and last_modified_date
        update_data = {
            "owner": new_owner_email,
            "last_modified_date": str(datetime.datetime.now())
        }

        # Update the collection
        update_result = self.collection.update_one(
            {"id": str(lambot_id)}, 
            {"$set": update_data}
        )

        if update_result.modified_count > 0:
            return {
                "message": "LamBot ownership successfully transferred.",
                "lambot_id": str(lambot_id),
                "new_owner": new_owner_email
            }
        else:
            raise RuntimeError("Failed to transfer LamBot ownership.")

    def delete_lambot(self, lambot_id: UUID) -> Dict[str, str]:
        """
        Delete a LamBot configuration from the MongoDB collection.

        Args:
            lambot_id (UUID): UUID of the LamBot configuration to delete.

        Returns:
            Dict[str, str]: A dictionary containing a success message or an error message.
        """
        is_deleted_result = self.collection.delete_one({"id": str(lambot_id)})
        
        if is_deleted_result.deleted_count > 0:
            return {"message": "LamBot configuration successfully deleted."}
        else:
            return {"message": "Failed to delete LamBot configuration."}
    
    def fetch_all_lambots(self, accessibility: LamBotConfigAccessibiltiy, tool_configs_list: List[ToolConfig], security_group_memberships_list: List[str], query_params=None) -> List[LamBotConfig]:
        """
        Fetch all LamBot configurations that the user has access to.

        Args:
            accessibility (LamBotConfigAccessibiltiy): Enum value representing whether to fetch accessible or non-accessible LamBots.
            tool_configs_list (List[ToolConfig]): List of ToolConfig instances representing the tools the user has access to.
            security_group_memberships_list (List[str]): List of security groups the user belongs to.
            query_params: Query parameters object containing displayName and filter criteria.

        Returns:
            List[LamBotConfig]: A list of LamBotConfig instances that the user has access to.
        """
        # Build MongoDB query with optional filters from query_params
        query = self._build_mongodb_query(query_params)

        # this is our default query to fetch all LamBots, we can override it with query_params
        current_user_email = user_email_var.get("email").lower()
        query["$or"] = [
            # Personal LamBots where owner field takes precedence
            {
                "personal": True,
                "$or": [
                    # Case 1: owner field exists and matches current user
                    {
                        "owner": {"$exists": True, "$ne": None, "$ne": ""},
                        "owner": current_user_email
                    },
                    # Case 2: owner field doesn't exist, is null, or is empty - check creator
                    {
                        "$or": [
                            {"owner": {"$exists": False}},
                            {"owner": None},
                            {"owner": ""}
                        ],
                        "creator": current_user_email
                    }
                ]
            },
            # Published LamBots (non-personal)
            {"personal": False},
            # Original LamBots without a personal field
            {"personal": {"$exists": False}}
        ]

        all_lambot_configs = self.collection.find(query)

        # Convert to list for processing
        lambot_list = list(all_lambot_configs)

        tool_access_list = [tool.name for tool in tool_configs_list if tool.user_has_access]

        # support for filtering by accessibility or retrieving all configs with user_has_access flag
        if accessibility == "accessible":
            filtered_lambot_configs = [config for config in lambot_list if access_condition_checks(config, security_group_memberships_list, tool_access_list)]
        elif accessibility == "non-accessible":
            filtered_lambot_configs = [config for config in lambot_list if not access_condition_checks(config, security_group_memberships_list, tool_access_list)]
        else:
            filtered_lambot_configs = []
            for config in lambot_list:
                if access_condition_checks(config, security_group_memberships_list, tool_access_list):
                    config["user_has_access"] = True
                else:
                    config["user_has_access"] = False
                filtered_lambot_configs.append(config)

        language_model_configs_list = self.language_model_config_service.fetch_all_language_models()

        # Convert results to LamBotConfig objects and update tools and selected_tools
        lambot_configs = package_lambot_config_with_tools(
            mongo_query_results=filtered_lambot_configs,
            tool_configs_list=tool_configs_list,
            language_model_configs_list=language_model_configs_list
        )
        
        return lambot_configs

    def _escape_regex_simple(self, text: str) -> str:
        """
        Escape special regex characters in search text for safe MongoDB regex queries.
        
        Args:
            text (str): Text to escape
            
        Returns:
            str: Escaped text safe for regex
        """
        import re
        return re.escape(text)

    def fetch_lambot(self, user_role: str, security_group_list: List[str], lambot_id: Optional[UUID] = None, display_name: Optional[str] = None, name: Optional[str] = None) -> Optional[LamBotConfig]:
        """
        Fetch a LamBot configuration by its UUID, display name, or unique name.
        Only one of lambot_id, display_name, or name should be provided.

        Args:
            lambot_id (Optional[UUID]): Optional UUID of the LamBot configuration to fetch.
            display_name (Optional[str]): Optional display name of the LamBot configuration to fetch.
            name (Optional[str]): Optional unique name of the LamBot configuration to fetch.
            user_role (str): The role of the user (e.g., "admin", "user", "creator").
            security_group_list (List[str]): The list of security groups the user belongs to.

        Returns:
            Optional[LamBotConfig]: A LamBotConfig instance if found, otherwise None.
        """
        provided = [v for v in [lambot_id, display_name, name] if v is not None]
        if len(provided) != 1:
            raise ValueError("You must provide exactly one of lambot_id, display_name, or name.")

        if lambot_id:
            query = {"id": str(lambot_id)}
        elif display_name:
            query = {"display_name": display_name}
        elif name:
            query = {"name": name}
        else:
            raise ValueError("One of lambot_id, display_name, or name must be provided.")

        return self._get_document_by_query(query, user_role, security_group_list)


    def check_tool_usage(self, tool_names: List[str]) -> dict:
        """
        Given a list of tool names, check which ones are used in any LamBotConfig.

        Args:
            tool_names (List[str]): List of tool names to check.

        Returns:
            dict: A dictionary where the key is the tool name and the corresponding value is a list of the LamBot config names that use the tool.
        """
         # Check if all tools exist in the ToolConfig collection
        all_tools_exist = self.tool_config_service.check_tools_exist(tool_names)

        if not all_tools_exist:
            raise ValueError("One or more of the provided tools could not be found")
        
        pipeline = [
            {
                '$match': {
                    'tools': {
                        '$in': tool_names
                    }
                }
            },
            {
                '$project': {
                    'display_name': 1,
                    'tools': 1
                }
            }
        ]

        results = self.collection.aggregate(pipeline)
        tool_usage = defaultdict(list)
        for document in results:
            for tool in document['tools']:
                if tool in tool_names:
                    tool_usage[tool].append(document['display_name'])              
        return dict(tool_usage)
    
    def check_language_model_usage(self, language_model_names: List[str]) -> dict:
        """
        Given a list of language model names, check which ones are used in any LamBotConfig.

        Args:
            language_model_names (List[str]): List of language model names to check.

        Returns:
            dict: A dictionary where the key is the language model name and the corresponding value is a list of the LamBot config names that use the language model.
        """
        # Check if all language models exist in the LanguageModelConfig collection
        all_language_models_exist = self.language_model_config_service.check_language_models_exist(language_model_names)

        if not all_language_models_exist:
            raise ValueError("One or more of the provided language models could not be found")

        pipeline = [
            {
                '$match': {
                    'supported_language_models.name': {
                        '$in': language_model_names
                    }
                }
            },
            {
                '$project': {
                    'display_name': 1,
                    'supported_language_models': 1
                }
            }
        ]

        results = self.collection.aggregate(pipeline)
        language_model_usage = defaultdict(list)
        for document in results:
            for language_model in document['supported_language_models']:
                if language_model['name'] in language_model_names:
                    language_model_usage[language_model['name']].append(document['display_name'])
        
        return dict(language_model_usage)

    def _build_mongodb_query(self, query_params) -> Dict[str, Any]:
        """
        Build MongoDB query based on query parameters.
        
        Args:
            query_params: LamBotConfigQueryParams object
            
        Returns:
            Dict[str, Any]: MongoDB query dictionary
        """

        # Default query: Include global LamBots, personal LamBots, and documents without a `personal` field
        query = {}

        if not query_params:
            return query
        
        # sonar hates string literals even if its for a query
        REGEX_STRING = "$regex"
        OPTIONS_STRING = "$options"

        if query_params.displayName:
            escaped_display_name = self._escape_regex_simple(query_params.displayName)
            query["display_name"] = {REGEX_STRING: escaped_display_name, OPTIONS_STRING: "i"}
            
        if query_params.creator:
            escaped_creator = self._escape_regex_simple(query_params.creator)
            query["creator"] = {REGEX_STRING: escaped_creator, OPTIONS_STRING: "i"}

        if query_params.personal is not None:
            # Convert Python boolean to MongoDB boolean
            query["personal"] = bool(query_params.personal)
        
        if query_params.name:
            query["name"] = query_params.name
            
        return query
    
    def _get_document_by_query(self, query, user_role, security_group_list):
        # Find the first matching document
        document = self.collection.find_one(query)
        
        if document:
            tool_configs_list = self.tool_config_service.fetch_tools(
                tool_names=document.get("tools", []),
                user_role=user_role,
                security_group_list=security_group_list
            )
            tool_access_list = [tool.name for tool in tool_configs_list if tool.user_has_access]
            if not access_condition_checks(document, security_group_list, tool_access_list):
                # Instead of returning None, raise a custom exception for 403 Forbidden
                raise NoAccessError("Forbidden: You do not have access to this LamBot configuration.")
            document.pop("_id", None)
            language_model_configs_list = self.language_model_config_service.fetch_all_language_models()
            lambot_config = package_lambot_config_with_tools(document, tool_configs_list, language_model_configs_list)
            return lambot_config
        return None

    def fetch_lambot_by_query_params(self, user_role: str, security_group_list: List[str], query_params) -> Optional[LamBotConfig]:
        """
        Fetch a single LamBot configuration based on query parameters.
        Returns the first accessible config matching the provided filters.

        Args:
            user_role (str): The role of the user (e.g., "admin", "user", "creator").
            security_group_list (List[str]): The list of security groups the user belongs to.
            query_params: LamBotConfigQueryParams object containing search criteria.

        Returns:
            Optional[LamBotConfig]: A LamBotConfig instance if found, otherwise None.
        """
        # Build MongoDB query with filters from query_params
        query = self._build_mongodb_query(query_params)

        return self._get_document_by_query(query, user_role, security_group_list)
