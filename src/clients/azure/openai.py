import os
import logging
from dotenv import load_dotenv
from openai import AzureOpenAI, AsyncAzureOpenAI
from src.clients.azure.token_generator import openai_token_provider

load_dotenv(override=True)

logger = logging.getLogger(__name__)

class AzureOpenAIClient:
    def __init__(self):
        """
        Initialize the AzureOpenAIClient with two clients: US and USE2.
        """
        if hasattr(self, '_initialized') and self._initialized:
            logger.info("AzureOpenAIClient is already initialized.")
            return

        # Load environment variables for US client
        endpoint_use = os.getenv("AZURE_OPENAI_ENDPOINT_USE")

        # Load environment variables for USE2 client
        endpoint_use2 = os.getenv("AZURE_OPENAI_ENDPOINT_USE2")

        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

        # Validate environment variables
        if not all([endpoint_use, endpoint_use2]):
            error_msg = "Azure OpenAI environment variables must be provided for both USE and USE2 clients."
            logger.error(error_msg)
            raise ValueError(error_msg)

        try:
            # Initialize USE client
            self.azure_use_region_client = AzureOpenAI(
                api_version=api_version,
                azure_endpoint=endpoint_use,
                azure_ad_token_provider=openai_token_provider,
            )
            logger.info("Azure OpenAI USE client initialized successfully.")

            self.async_azure_use_region_client = AsyncAzureOpenAI(
                api_version=api_version,
                azure_endpoint=endpoint_use,
                azure_ad_token_provider=openai_token_provider,
            )   
            logger.info("Azure OpenAI USE async client initialized successfully.")

            # Initialize USE2 client
            self.azure_use2_region_client = AzureOpenAI(
                azure_endpoint=endpoint_use2,
                api_version=api_version,
                azure_ad_token_provider=openai_token_provider,
            )
            logger.info("Azure OpenAI USE2 client initialized successfully.")

            self.async_azure_use2_region_client = AsyncAzureOpenAI(
                azure_endpoint=endpoint_use2,
                api_version=api_version,
                azure_ad_token_provider=openai_token_provider,
            )
            logger.info("Azure OpenAI USE2 async client initialized successfully.")

            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize AzureOpenAIClient: {e}")
            raise

    def shutdown(self):
        """
        Shutdown the AzureOpenAIClient.
        """
        self.azure_use_region_client.close()
        self.azure_use2_region_client.close()
        logger.info("AzureOpenAIClient shutdown completed.")
