import os
import uuid
from datetime import datetime, timedelta, timezone
from src.clients import LifespanClients
from azure.storage.blob import generate_blob_sas, BlobSasPermissions

def get_prompt(prompt_name: str, fallback_prompt: str, label: str = "dev") -> str:
    """Fetches a prompt from LangfuseManager or uses a fallback prompt.

    Args:
        prompt_name (str): The name of the prompt to fetch.
        fallback_prompt (str): The fallback prompt to use if the prompt is not found.
        label (str, optional): The label for the prompt. Defaults to "dev".

    Returns:
        str: The fetched prompt.
    """
    return LifespanClients.get_instance().langfuse_manager.get_prompt(
        prompt_name=prompt_name,
        fallback_prompt=fallback_prompt,
        label=label
    )

def upload_data_to_adls(tool_name: str, file_bytes: bytes, expiry: timedelta = timedelta(weeks=12), file_name: str = None) -> str:
    """Uploads a file to ADLS and generates a SAS URL.

    Args:
        tool_name (str): The name of the tool.
        file_bytes (bytes): The byte content of the file to upload.
        expiry (timedelta, optional): The expiry time of the link. Defaults to timedelta(weeks=12).
        file_name (str, optional): The name of the file to upload. If not provided, a UUID will be used.

    Returns:
        str: The downloadable link.
    """

    lifespan_clients = LifespanClients.get_instance()

    # Generate a unique blob name
    if file_name:
        blob_name = f"tools/{tool_name}/tool_artifact_files/{str(uuid.uuid4())}_{file_name}"
    else:
        blob_name = f"tools/{tool_name}/tool_artifact_files/{str(uuid.uuid4())}"


    container_name = os.getenv("AZURE_BLOB_STORAGE_CONTAINER_NAME", "lambots")

    # Upload the blob
    lifespan_clients.container.upload_blob(name=blob_name, data=file_bytes)

    # Generate a SAS URL for the blob
    sas_token = generate_blob_sas(
        account_name=lifespan_clients.blob_service.account_name,
        container_name=container_name,
        blob_name=blob_name,
        account_key=lifespan_clients.blob_service.credential.account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.now(timezone.utc) + expiry
    )

    # Construct the full URL
    blob_url = f"https://{lifespan_clients.blob_service.account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"

    return blob_url