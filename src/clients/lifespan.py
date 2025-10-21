import os
import logging
from dotenv import load_dotenv
from src.clients.mongo import MongoDBClient
from src.clients.synapse import SynapseClient
from src.clients.azure.openai import AzureOpenAIClient
from azure.storage.blob import BlobServiceClient
from src.clients.redis import RedisClient
from src.clients.langfuse.manager import LangfuseManager
from src.clients.langfuse.manager_sensitive import LangfuseManagerSensitive
from src.clients.langfuse.manager_redacted import LangfuseManagerRedacted
from src.clients.azure.ai_foundry_agent import AzureAIFoundryAgentClient

load_dotenv(override=True)

# Configure logging with a custom format including timestamp, logger name, log level, and message
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class LifespanClients:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(LifespanClients, cls).__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        """
        Initialize the LifespanServices with necessary configurations.
        """
        # Prevent reinitialization in case __init__ is called more than once.
        if hasattr(self, '_initialized') and self._initialized:
            logger.info("LifespanServices is already initialized.")
            return
        logger.info("Initializing LifespanServices.")

        self.mongo_db = MongoDBClient.get_instance()
        self.langfuse_manager = LangfuseManager.get_instance()
        self.langfuse_manager_sensitive = LangfuseManagerSensitive.get_instance()
        self.langfuse_manager_redacted = LangfuseManagerRedacted.get_instance()

        self.synapse = SynapseClient.get_instance()
        self.azure_openai = AzureOpenAIClient()
        self.redis = RedisClient.get_instance()        
        
        # SPN-based keyless authentication for Azure Blob Storage
        self.blob_service = BlobServiceClient.from_connection_string(os.getenv("AZURE_BLOB_STORAGE_CONNECTION_STRING"))
        self.container = self.blob_service.get_container_client(container=os.getenv("AZURE_BLOB_STORAGE_CONTAINER_NAME", "lambots"))
        
        self.azure_ai_foundry_agent = AzureAIFoundryAgentClient.get_instance()
        
        logger.info("LifespanServices instantiated successfully.")
        self._initialized = True

    @classmethod
    def get_instance(cls) -> "LifespanClients":
        """
        Retrieve the singleton instance of LifespanServices.
        """
        if cls._instance is None:
            cls._instance = LifespanClients()
        return cls._instance

    async def shutdown(self) -> None:
        """
        Shut down the services gracefully.
        """
        logger.info("Shutting down LifespanServices.")
        self.mongo_db.shutdown()
        self.synapse.shutdown()
        self.azure_openai.shutdown()
        self.redis.shutdown()
        self.blob_service.close()
        self.container.close()
        self.azure_ai_foundry_agent.shutdown()
        logger.info("LifespanServices shut down.")