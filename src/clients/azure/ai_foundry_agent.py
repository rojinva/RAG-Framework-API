import os
import logging

from azure.identity import ClientSecretCredential
from azure.ai.agents import AgentsClient

from dotenv import load_dotenv
load_dotenv(override=True)

logger = logging.getLogger(__name__)


class AzureAIFoundryAgentClient:
    _instance = None

    @classmethod
    def get_instance(cls):
        """
        Retrieve the singleton instance of AzureAIFoundryAgentClient.
        """
        if cls._instance is None:
            cls._instance = AzureAIFoundryAgentClient()
        return cls._instance

    def __init__(self):
        """
        Initialize the AzureAIFoundryAgentClient with an AgentsClient instance.
        """
        if hasattr(self, "_initialized") and self._initialized:
            logger.info("AzureAIFoundryAgentClient is already initialized.")
            return

        try:
            # Create the credential object
            cred = ClientSecretCredential(
                tenant_id=os.getenv("LAMBOTS_TENANT_ID"),
                client_id=os.getenv("LAMBOTS_CLIENT_ID"),
                client_secret=os.getenv("LAMBOTS_CLIENT_SECRET"),
            )

            # Initialize the AgentsClient
            self.agent_client = AgentsClient(
                endpoint=os.getenv("AZURE_AI_FOUNDRY_ENDPOINT"),
                credential=cred,
            )
            logger.info("AzureAIFoundryAgentClient initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize AzureAIFoundryAgentClient: {e}")
            raise

        self._initialized = True

    def shutdown(self):
        """
        Perform any necessary cleanup
        """

        self.agent_client.close()
        logger.info("AzureAIFoundryAgentClient shutdown completed.")
