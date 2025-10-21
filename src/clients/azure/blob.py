from azure.storage.blob import BlobServiceClient
import os
import logging
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential

load_dotenv(override=True)
logger = logging.getLogger(__name__)

class AzureBlobStorageClient:
    _instance = None

    @classmethod
    def get_instance(cls):
        """
        Get the singleton instance of AzureBlobStorageClient.
        This method implements the singleton pattern to ensure only one instance
        of the AzureBlobStorageClient exists throughout the application lifecycle.
        Returns:
            AzureBlobStorageClient: The singleton instance of the Azure Blob Storage client.
                If no instance exists, creates a new one; otherwise returns the existing instance.
        """
        
        if cls._instance is None:
            cls._instance = AzureBlobStorageClient()
        return cls._instance
    
    def __init__(self):
        """
        Initialize the AzureBlobStorageClient with Azure credentials and blob service configuration.
        This method sets up the Azure Blob Storage client using service principal authentication
        with credentials from environment variables. It creates a blob service client and 
        container client for interacting with Azure Blob Storage.
        Environment Variables Required:
            LAMBOTS_TENANT_ID: Azure AD tenant ID
            LAMBOTS_CLIENT_ID: Azure AD application (client) ID
            LAMBOTS_CLIENT_SECRET: Azure AD application client secret
            AZURE_BLOB_STORAGE_ACCOUNT_NAME: Name of the Azure Storage account
            AZURE_BLOB_STORAGE_CONTAINER_NAME: Name of the blob container
        Raises:
            Exception: If initialization fails due to invalid credentials, missing environment
                      variables, or connection issues with Azure Blob Storage.
        Note:
            This method implements a singleton-like pattern to prevent re-initialization
            if the client has already been successfully initialized.
        """
        
        if hasattr(self, "_initialized") and self._initialized:
            logger.info("AzureBlobStorageClient is already initialized.")
            return
        try:
            credential = ClientSecretCredential(
                tenant_id=os.getenv("LAMBOTS_TENANT_ID"),
                client_id=os.getenv("LAMBOTS_CLIENT_ID"),
                client_secret=os.getenv("LAMBOTS_CLIENT_SECRET"),
            )
            blob_account_url = f"https://{os.getenv('AZURE_BLOB_STORAGE_ACCOUNT_NAME')}.blob.core.windows.net"
            self.blob_service_client = BlobServiceClient(account_url=blob_account_url, credential=credential)
            self.container = self.blob_service_client.get_container_client(container=os.getenv("AZURE_BLOB_STORAGE_CONTAINER_NAME"))
            logger.info("AzureBlobStorageClient initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize AzureBlobStorageClient: {e}")
            raise
        self._initialized = True

    def shutdown(self):
        """
        Properly shuts down the Azure Blob Storage client by closing the connection.
        This method performs cleanup operations by closing the blob service client
        connection and logs the completion of the shutdown process.
        Returns:
            None
        """
        
        self.blob_service_client.close()
        logger.info("AzureBlobStorageClient shutdown completed.")