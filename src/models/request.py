from pydantic import Field
from src.models.base import ConfiguredBaseModel
from src.models.constants import MimeType
from src.models.config import QueryConfig
from typing import List, Optional, Literal

class MessageFile(ConfiguredBaseModel):
    """Model representing a file attachment in a chat request"""
    type: Literal["hash", "base64"] = Field(
        ..., description="Type of file reference - hash for a stored file or base64 for inline content"
    )
    name: str = Field(..., description="Filename of the attachment")
    value: str = Field(..., description="Hash reference or base64-encoded content of the file")
    mime: MimeType = Field(..., description="MIME type of the file")


class LamBotChatRequest(ConfiguredBaseModel):
    lambot_id: str = Field(..., description="ID for the LamBot.")
    query_config: Optional[QueryConfig] = Field(
        None,
        description="Optional configuration for the query. If not provided, defaults to None.",
    )
    messages: List[dict] = Field(
        ..., description="Conversation messages to be processed by the LamBot."
    )
    file_attachments: Optional[List[MessageFile]] = Field(
        None, description="Optional file attachments for the chat request"
    )

class LamBotChatRequestExternal(ConfiguredBaseModel):

    lambot_id: str = Field(..., description="ID for the LamBot.")
    thread_id: Optional[str] = Field(None, description="thread_id  for the LamBot (optional).")
    query_config: Optional[QueryConfig] = Field(
        None,
        description="Optional configuration object to influence query behavior.",
    )
    messages: List[dict] = Field(..., description="Conversation messages to be processed by the LamBot.")