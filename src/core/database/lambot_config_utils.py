from src.models.config import LamBotConfig
from pydantic import AnyUrl

def package_lambot_config_with_tools(mongo_query_results, tool_configs_list, language_model_configs_list):
    """
    Packages LamBot configurations by mapping tool names to their configurations.

    Args:
        mongo_query_results (dict or list): The result(s) from a MongoDB collection query.
                                            It can be a single document (dict) or a list of documents (list of dicts).
        tool_configs_list (list): A list of tool configs.
        language_model_configs_list (list): A list of language model configs.

    Returns:
        LamBotConfig or list: A single LamBotConfig object if mongo_query_results is a single document,
                              or a list of LamBotConfig if mongo_query_results is a list of documents.

    Raises:
        ValueError: If mongo_query_results is neither a dictionary nor a list of dictionaries.
    """
    # Create a mapping of tool names to their configurations
    tool_configs_mapping = {tool.name: tool for tool in tool_configs_list}

    # Create a mapping of language model names to their configurations
    language_model_configs_mapping = {lm.name: lm for lm in language_model_configs_list}

    def package_single_lambot_config(document):
        """
        Packages a single LamBot config document.

        Args:
            document (dict): A single LamBot config document.

        Returns:
            LamBotConfig: The packaged LamBot config.
        """
        # Extract tools and selected_tools directly
        document["tools"] = [
            tool_configs_mapping[tool]
            for tool in document.get("tools", [])
        ]

        document["default_query_config"]["selected_tools"] = [
            tool_configs_mapping[tool]
            for tool in document["default_query_config"].get("selected_tools", [])
        ]

        # Replace the language model in default_query_config
        language_model_name = document["default_query_config"]["language_model"]
        document["default_query_config"]["language_model"] = language_model_configs_mapping.get(language_model_name)

        # Replace the supported language models, adding only if not None
        document["supported_language_models"] = [
            lm for language_model_name in document.get("supported_language_models", [])
            if (lm := language_model_configs_mapping.get(language_model_name)) is not None
        ]
        if document["default_query_config"]["language_model"] is None:
            document["default_query_config"]["language_model"] = document["supported_language_models"][0] if document["supported_language_models"] else None

        # Convert sharepoint_urls strings back to AnyUrl objects
        if document.get("sharepoint_urls"):
            document["sharepoint_urls"] = [AnyUrl(url) for url in document["sharepoint_urls"]]
        
        # Package the LamBot configuration
        return LamBotConfig(**document)

    # Check if mongo_query_results is a single document or a list of documents
    if isinstance(mongo_query_results, dict):
        return package_single_lambot_config(mongo_query_results)
    elif isinstance(mongo_query_results, list):
        return [
            package_single_lambot_config(document) for document in mongo_query_results
        ]
    else:
        raise ValueError(
            "Invalid mongo_query_results type. Expected a dictionary or a list of dictionaries."
        )
