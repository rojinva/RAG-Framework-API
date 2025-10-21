from dotenv import load_dotenv
from typing import List
from pymongo.collection import Collection

from src.models.config import LanguageModelConfig
from src.core.database.lambot_config import LamBotConfigDB
from src.core.cache.decorators import cache_platform, cache_platform_with_args, invalidate_platform_cache

load_dotenv()


class LanguageModelConfigDB:
    def __init__(self, collection: Collection, lambot_config_db: LamBotConfigDB):
        self.collection = collection
        self.lambot_config_db = lambot_config_db

    def fetch_all_language_models(self) -> List[LanguageModelConfig]:
        """
        Fetch all LanguageModelConfig objects from the collection.

        Returns:
            List[LanguageModelConfig]: List of all LanguageModelConfig objects.
        """
        # Get cached raw dictionaries
        language_model_dicts = self._fetch_all_language_model_dicts_cached()
        # Convert to LanguageModelConfig objects
        return [LanguageModelConfig(**doc) for doc in language_model_dicts]
    
    @cache_platform("all_language_models_dicts", ttl=3600)
    def _fetch_all_language_model_dicts_cached(self) -> List[dict]:
        """
        Cached method to fetch all language models as dictionaries from MongoDB.
        Returns raw dictionaries that are JSON serializable for Redis caching.
        """
        language_model_dicts = []
        for document in self.collection.find():
            document.pop("_id")
            language_model_dicts.append(document)
        return language_model_dicts

    def fetch_all_language_model_keys(self) -> List[str]:
        """
        Fetch all LanguageModelConfig keys from the database.

        Returns:
            List[str]: List of keys for all LanguageModelConfig objects.
        """
        language_models = self.fetch_all_language_models()
        return [model.name for model in language_models]

    def add_language_model(self, language_model_config: LanguageModelConfig) -> LanguageModelConfig:
        """
        Add a new LanguageModelConfig to the collection.

        Args:
            language_model_config (LanguageModelConfig): The configuration to add.

        Returns:
            LanguageModelConfig: The added LanguageModelConfig object.
        """
        # Check if a language model with the same name or display name already exists
        existing_language_model = self.collection.find_one({
            "$or": [
                {"name": language_model_config.name},
                {"display_name": language_model_config.display_name}
            ]
        })
        if existing_language_model:
            raise ValueError("A language model with the same name or display name already exists.")
        
        document = language_model_config.model_dump()
        result = self.collection.insert_one(document)
        inserted_document = self.collection.find_one({"_id": result.inserted_id})
        inserted_document.pop("_id")

        # Invalidate cache since we added a new model
        self._invalidate_language_model_cache()

        return LanguageModelConfig(**inserted_document)

    def update_language_model(self, language_model_name: str, language_model_config: LanguageModelConfig) -> LanguageModelConfig:
        """
        Updates the configuration of an existing language model.

        Args:
            language_model_name (str): The name of the language model to update.
            language_model_config (LanguageModelConfig): The new configuration for the language model.

        Returns:
            LanguageModelConfig: The updated language model configuration.

        Raises:
            ValueError: If the language model configuration is not found.
            ValueError: If the language model name is modified.
            ValueError: If a language model with the same display name already exists.
            ValueError: If no changes were made to the language model configuration.
        """
        # Get the language model to update
        old_language_model_config = self.fetch_language_model(language_model_name=language_model_name)
        if not old_language_model_config:
            raise ValueError("LanguageModelConfig not found")

        # Check that user has not attempted to modify the language model name
        if language_model_name != language_model_config.name:
            raise ValueError("Language model name cannot be modified.")
        
        # Check that the display name is unique
        existing_language_model_display_name = self.collection.find_one({"display_name": language_model_config.display_name})
        if existing_language_model_display_name:
            raise ValueError("A language model with the same display name already exists. Display names must be unique.")

        # Update the language model configuration
        update_result = self.collection.update_one(
            {"name": language_model_name},
            {"$set": language_model_config.model_dump()}
        )

        if update_result.modified_count == 0:
            raise ValueError("No changes were made to the language model configuration")

        updated_document = self.collection.find_one({"name": language_model_name})
        updated_document.pop("_id")

        # Invalidate cache since we updated a model
        self._invalidate_language_model_cache()

        return LanguageModelConfig(**updated_document)

    def delete_language_model(self, language_model_name: str) -> bool:
        """
        Delete a language model from the collection.

        Args:
            language_model_name (str): Name of the language model to delete.

        Returns:
            bool: True if the language model was successfully deleted, False otherwise.
        """
        # Check if the requested language model exists
        language_model_exists = self.fetch_language_model(language_model_name=language_model_name)
        if not language_model_exists:
            raise ValueError("LanguageModelConfig not found")
        
        # Check if the language model is used in any LamBot configurations
        language_model_usage = self.lambot_config_db.check_language_model_usage([language_model_name])
        if language_model_usage:
            raise ValueError(f"Deleting a language model config that is currently being used is forbidden. The following language model(s) are being used by the corresponding LamBot(s): {language_model_usage}")
        
        is_deleted_result = self.collection.delete_one({"name": language_model_name})
        
        if is_deleted_result.deleted_count > 0:
            # Invalidate cache since we deleted a model
            self._invalidate_language_model_cache()
            return True
        else:
            return False

    @cache_platform_with_args("language_model:{language_model_name}", ttl=3600, return_type=LanguageModelConfig)
    def fetch_language_model(self, language_model_name: str) -> LanguageModelConfig:
        """
        Fetch a LanguageModelConfig object from the collection based on the language model name.

        Args:
            language_model_name (str): Name of the language model to fetch.

        Returns:
            LanguageModelConfig: The fetched LanguageModelConfig object.
        """
        query = {"name": language_model_name}
        document = self.collection.find_one(query)
        
        if not document:
            raise ValueError(f"No language model with the name {language_model_name} could be found.")
        document.pop("_id", None)

        return LanguageModelConfig(**document)

    def check_language_models_exist(self, language_model_names: List[str]) -> bool:
        """
        Check if all language models in the list exist in the collection.

        Args:
            language_model_names (List[str]): List of language model names to check.

        Returns:
            bool: True if all language models exist, False otherwise.
        """
        all_model_names = self.fetch_all_language_model_keys()
        return set(language_model_names).issubset(set(all_model_names))

    def _invalidate_language_model_cache(self):
        """
        Invalidate all cached language model data.
        """
        invalidate_platform_cache(
            keys=["all_language_models_dicts"],
            patterns=["language_model:*"]
        )

