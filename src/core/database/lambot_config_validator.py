from src.models.config import LamBotConfig
from typing import Dict, Any


class LamBotConfigValidator:
    """Centralizes all validation logic for LamBot configurations"""
    
    def __init__(self, language_model_config_service):
        self.language_model_config_service = language_model_config_service
    
    def validate_for_write(self, lambot_config: LamBotConfig) -> Dict[str, Any]:
        """Validates a LamBot configuration before creation"""
        # Check if language model in default_query_config is in supported_language_models
        if not self._is_default_language_model_supported(lambot_config):
            return {"valid": False, "message": "The language model in the default query configuration is not in the supported language models."}
            
        # Check if all supported language models exist
        language_model_names = [llm.name for llm in lambot_config.supported_language_models]
        if not self.language_model_config_service.check_language_models_exist(language_model_names):
            return {"valid": False, "message": "One or more supported language models could not be found in the LanguageModelConfig collection."}
            
        # Check if all tools in tool_categories are in the tools list
        tool_categories_validation = self._validate_tool_categories(lambot_config)
        if not tool_categories_validation["valid"]:
            return tool_categories_validation
            
        return {"valid": True}
    
    def _is_default_language_model_supported(self, lambot_config: LamBotConfig) -> bool:
        """Checks if the default language model is in supported language models"""
        default_model = lambot_config.default_query_config.language_model
        return any(llm.name == default_model.name for llm in lambot_config.supported_language_models)
    
    def _validate_tool_categories(self, lambot_config: LamBotConfig) -> Dict[str, Any]:
        """Validates that all tools referenced in tool_categories exist in the tools list"""
        if not lambot_config.tool_categories:
            return {"valid": True}  # No tool categories to validate
            
        # Get all tool names from the tools list
        tool_names = {tool.name for tool in lambot_config.tools}
        
        # Check each tool in each category
        for category, tools_in_category in lambot_config.tool_categories.items():
            for tool_name in tools_in_category:
                if tool_name not in tool_names:
                    return {
                        "valid": False,
                        "message": f"Tool '{tool_name}' in category '{category}' is not in the tools list"
                    }
        
        return {"valid": True}
