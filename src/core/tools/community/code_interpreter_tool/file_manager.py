import io
import base64
import logging

from typing import Dict, List
from src.models.request import MessageFile
from src.core.tools.community.code_interpreter_tool.models import AssistantFile
from src.clients import LifespanClients
from openai.types.beta.threads.image_file_content_block import ImageFileContentBlock
from openai.types.beta.threads.image_url_content_block import ImageURLContentBlock


class AssistantFileManager:
    """
    Manages file uploads and attachments for OpenAI Assistant.
    Provides methods to upload files from bytes or file paths and get file IDs.
    """

    def __init__(self):
        self.client = (
            LifespanClients.get_instance().azure_openai.azure_use2_region_client
        )

    async def upload_files_to_assistant(
        self, message_files: List[MessageFile]
    ) -> Dict[str, str]:
        """
        Upload files from MessageFile objects to the OpenAI Assistant.

        Args:
            message_files: List of MessageFile objects

        Returns:
            A dictionary mapping file names to their corresponding file IDs.
        """
        _file_mappings = {}
        for message_file in message_files:
            try:
                if message_file.type == "base64":
                    file_bytes = base64.b64decode(message_file.value)
                    file_obj = io.BytesIO(file_bytes)
                    file_obj.name = message_file.name
                    file = self.client.files.create(file=file_obj, purpose="assistants")
                    logging.info(f"File uploaded successfully. File ID: {file.id}")
                    _file_mappings[message_file.name] = (
                        file.id
                    )  # Map file name to file ID
                else:
                    logging.warning(f"Unsupported file type: {message_file.type}")
            except Exception as e:
                logging.error(f"Failed to upload file {message_file.name}: {str(e)}")
        return _file_mappings

    async def delete_files(self, file_mappings: Dict[str, str]) -> None:
        """
        Delete uploaded files.
        Args:
            file_mappings: A dictionary mapping file names to their corresponding file IDs.
        """
        for _, file_id in file_mappings.items():
            try:
                self.client.files.delete(file_id)
                logging.info(f"File deleted successfully. File ID: {file_id}")
            except Exception as e:
                logging.error(f"Failed to delete file {file_id}: {str(e)}")

    async def get_files_from_thread(self, thread_id: str) -> List[AssistantFile]:
        """
        Retrieve files associated with a specific thread.

        Args:
            thread_id: The ID of the thread to retrieve files from.

        Returns:
            List[AssistantFile]: A list of AssistantFile objects.
        """
        files = []
        messages = self.client.beta.threads.messages.list(thread_id=thread_id)

        for message in messages:
            if not message.content:
                continue

            for content in message.content:
                # Skip image content blocks since images are being dispatched separately in RunSteps
                if isinstance(content, ImageFileContentBlock) or isinstance(content, ImageURLContentBlock):
                    continue

                if not content.text:
                    continue

                for annotation in content.text.annotations:
                    if annotation.type != "file_path":
                        continue

                    try:
                        file_response = self.client.files.content(
                            file_id=annotation.file_path.file_id
                        )
                        file_bytes = file_response.read()

                        raw_file_name = (
                            annotation.text
                        )  # Example: sandbox:/mnt/data/car_sales_dummy_data.xlsx

                        files.append(
                            AssistantFile(
                                file_name=raw_file_name.split("/")[
                                    -1
                                ],  # Extract the file name from the path
                                file_bytes=file_bytes,
                            )
                        )
                    except Exception as e:
                        logging.error(f"Failed to process file annotation: {str(e)}")

        return files
