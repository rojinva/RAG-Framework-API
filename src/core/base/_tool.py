from langchain_core.tools import BaseTool
from src.models import ToolType
from src.core.base import LamBotEvents
from src.models.tool import ToolArtifact, ToolKwargs
from src.models.constants import IntakeItem
from azure.storage.blob import generate_blob_sas, BlobSasPermissions
from src.clients import LifespanClients
from langchain_core.callbacks.manager import dispatch_custom_event
from datetime import datetime, timedelta, timezone
import uuid
import os
import asyncio
import pandas as pd
from io import BytesIO
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from pydantic import Field
from typing import List, Optional, Any
from src.core.base.utils import get_prompt

from dotenv import load_dotenv
load_dotenv(override=True)


class LamBotTool(BaseTool, LamBotEvents):
    """LamBotTool that includes an additional parameter called tool_type."""

    tool_type: ToolType
    allowed_intakes: Optional[List[IntakeItem]] = Field(
        default=None,
        description="List of allowed intake items for this tool."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._conversation_history = None  # Initialize conversation history attribute
        self._file_attachments = None  # Initialize file attachments attribute
        self._tool_kwargs = None  # Initialize tool keyword arguments attribute
        self._lock = asyncio.Lock()  # Add an asyncio lock for thread-safe updates

    @staticmethod
    def dispatch_tool_artifact(tool_artifact: ToolArtifact):
        """Dispatches a custom event with the tool artifact.

        Args:
            tool_artifact (ToolArtifact): The tool artifact to dispatch.
        """
        dispatch_custom_event(
            name="tool_artifact",
            data={"artifact": tool_artifact},
        )

    def upload_dataframe_to_adls(self, dataframe: pd.DataFrame, expiry: timedelta = timedelta(weeks=12), file_name: str = None) -> str:
        """Uploads a pd.DataFrame to ADLS as an XLSX file and generates a SAS URL.

        Args:
            dataframe (pd.DataFrame): The dataframe to upload.
            expiry (timedelta, optional): The expiry time of the link. Defaults to timedelta(weeks=12).

        Returns:
            str: The downloadable link.
        """

        lifespan_clients = LifespanClients.get_instance()

        # Generate a unique blob name
        if file_name:
            blob_name = f"tools/{self.name}/tool_artifact_files/{file_name}.xlsx"
        else:
            blob_name = f"tools/{self.name}/tool_artifact_files/{uuid.uuid4()}.xlsx"

        # Clean the DataFrame by removing illegal characters
        clean_dataframe = dataframe.applymap(lambda x: ILLEGAL_CHARACTERS_RE.sub("", x) if isinstance(x, str) else x)

        # Save the dataframe to a buffer
        buffer = BytesIO()
        clean_dataframe.to_excel(buffer, index=False)
        buffer.seek(0)

        # Create a BlobServiceClient
        blob_service_client = lifespan_clients.blob_service

        # Get a container client
        container_name = os.getenv("AZURE_BLOB_STORAGE_CONTAINER_NAME", "lambots")
        container_client = lifespan_clients.container

        # Upload the blob
        container_client.upload_blob(name=blob_name, data=buffer)

        # Close the buffer to free up memory
        buffer.close()

        # Generate a SAS URL for the blob
        sas_token = generate_blob_sas(
            account_name=blob_service_client.account_name,
            container_name=container_name,
            blob_name=blob_name,
            account_key=blob_service_client.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.now(timezone.utc) + expiry
        )

        # Construct the full URL
        blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"

        return blob_url
    
    @staticmethod
    def _get_prompt(prompt_name: str, fallback_prompt: str, label: str) -> str:
        """Fetches a prompt from LangfuseManager or uses a fallback prompt.

        Args:
            prompt_name (str): The name of the prompt to fetch.
            fallback_prompt (str): The fallback prompt to use if the prompt is not found.
            label (str): The label for the prompt in Langfuse.

        Returns:
            str: The fetched prompt.
        """
        return get_prompt(prompt_name, fallback_prompt, label)
    
    # Setter for conversation history
    async def set_conversation_history(self, conversation_history: List[dict]):
        """
        Set the conversation history attribute in a thread-safe manner.
        :param conversation_history: List of messages in {role, content} format.
        """
        async with self._lock:  # Acquire the lock
            self._conversation_history = conversation_history

    # Getter for conversation history
    async def get_conversation_history(self) -> Optional[List[dict]]:
        """
        Get the conversation history attribute in a thread-safe manner.
        :return: List of messages in {role, content} format.
        """
        async with self._lock:  # Acquire the lock
            return self._conversation_history

    # Setter for file attachments
    async def set_file_attachments(self, file_attachments: List[Any]):
        """
        Set the file attachments attribute in a thread-safe manner.
        :param file_attachments: List of file attachments to be processed by the tool.
        """
        async with self._lock:  # Acquire the lock
            self._file_attachments = file_attachments

    # Getter for file attachments
    async def get_file_attachments(self) -> Optional[List[Any]]:
        """
        Get the file attachments attribute in a thread-safe manner.
        :return: List of file attachments to be processed by the tool.
        """
        async with self._lock:  # Acquire the lock
            return self._file_attachments
        
    # Setter for tool keyword arguments
    def set_tool_kwargs(self, tool_kwargs: Optional[dict[str, Any]]):
        """
        Set the tool keyword arguments attribute.
        :param tool_kwargs: dictionary containing keyword arguments for the tool.
        """
        if tool_kwargs is None:
            self._tool_kwargs = None
        else:
            self._tool_kwargs = ToolKwargs.from_data(**tool_kwargs)

    # Getter for tool keyword arguments
    def get_tool_kwargs(self) -> Optional[dict[str, Any]]:
        """
        Get the tool keyword arguments attribute.
        :return: dictionary containing keyword arguments for the tool.
        """
        if self._tool_kwargs is None:
            return None
        return self._tool_kwargs.model_dump()
    
    # Getter for specific tool keyword argument
    def get_tool_kwarg(self, key: str, default: Any = None) -> Any:
        """
        Get a specific tool keyword argument.
        :param key: The key to retrieve.
        :param default: Default value if key is not found.
        :return: The value for the specified key or default.
        """
        if self._tool_kwargs is None:
            return default
        return self._tool_kwargs.model_dump().get(key, default)