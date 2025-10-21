from pymongo.collection import Collection
from src.clients.mongo import MongoDBClient
from src.core.database.lambot_config import LamBotConfigDB
from src.core.database.tools import ToolConfigDB
from src.core.database.language_model_config import LanguageModelConfigDB
from src.core.database.lambot_config_validator import LamBotConfigValidator
from src.core.database.thread import ThreadDB

from dotenv import load_dotenv
load_dotenv()


class LamBotMongoDB:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = LamBotMongoDB()
        return cls._instance

    def __init__(self) -> None:
        """
        Initializes the LamBotMongoDB by creating a single MongoDBClient instance
        and reusing it to query multiple collections from a given database.
        """
        self.mongo = MongoDBClient.get_instance()

        # Initialize MongoDBService instances with provided parameters
        TOOL_CONFIGS_COLLECTION_NAME = "toolConfigs"
        LAMBOT_CONFIGS_COLLECTION_NAME = "lambotConfigs"
        LANGUAGE_MODEL_CONFIGS_COLLECTION_NAME = "languageModelConfigs"
        CONVERSATIONS_EXTERNAL_COLLECTION_NAME = "conversationsExternal"
        
        tool_config_collection = Collection(
            database=self.mongo.database,
            name=TOOL_CONFIGS_COLLECTION_NAME,
        )

        lambot_config_collection = Collection(
            database=self.mongo.database,
            name=LAMBOT_CONFIGS_COLLECTION_NAME,
        )

        language_model_config_collection = Collection(
            database=self.mongo.database,
            name=LANGUAGE_MODEL_CONFIGS_COLLECTION_NAME,
        )

        conversations_external_collection = Collection(
            database=self.mongo.database,
            name=CONVERSATIONS_EXTERNAL_COLLECTION_NAME,
        )
        
        # Initialize services
        self.lambot_config_db = LamBotConfigDB(collection=lambot_config_collection)
        self.tool_config_db = ToolConfigDB(collection=tool_config_collection, lambot_config_db=self.lambot_config_db)
        self.language_model_config_db = LanguageModelConfigDB(collection=language_model_config_collection, lambot_config_db=self.lambot_config_db)
        # Overwrite/update list of llm config as part initialization
        self.language_model_config_db.fetch_all_language_models()
        self.conversations_external_db = ThreadDB(collection=conversations_external_collection)

        # Inject ToolConfigService into LamBotConfigService if needed
        self.lambot_config_db.tool_config_service = self.tool_config_db
        self.lambot_config_db.language_model_config_service = self.language_model_config_db
        self.lambot_config_db.validator = LamBotConfigValidator(self.language_model_config_db)

    def shutdown(self) -> None:
        """
        Shuts down the MongoDBClient by closing its connection.
        """
        self.mongo.shutdown()
