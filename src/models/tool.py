from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_snake
from src.models.base import ConfiguredBaseModel
from typing import Optional

from src.models.constants import MimeType


class ToolArtifact(ConfiguredBaseModel):
    content: str = Field(..., description="Content of the artifact.")
    display_name: str = Field(..., description="Display name of the artifact.")
    tool_name: str = Field(..., description="Name of tool that generated the artifact.")
    url: Optional[str] = Field(None, description="URL associated with the artifact.")
    url_display_name: Optional[str] = Field(None, description="Display name of URL associated with the artifact.")
    content_type: Optional[MimeType] = Field(None, description="MIME type or content type of the artifact (e.g., 'image/png', 'text/plain', 'application/python')")
    is_downloadable: Optional[bool] = Field(None, description="Whether this artifact should be downloadable")
    preview_url: Optional[str] = Field(None, description="URL for previewing the artifact (for images, videos, etc.)")

    def __hash__(self):
        return hash(self.content)  # Hash based on content

    def __eq__(self, other):
        if isinstance(other, ToolArtifact):
            return self.content == other.content  # Equality based on content
        return False


class ToolKwargs(BaseModel):
    """
    A flexible model for arbitrary keyword arguments passed to tools.

    This model allows any extra fields, making it suitable for dynamic or tool-specific parameters
    without requiring explicit field definitions. It also supports camelCase to snake_case key conversion
    via the from_data() method.
    """
    # Allow extra fields for arbitrary tool keyword arguments.
    model_config = ConfigDict(extra="allow")

    # Convert camelCase keys to snake_case.
    # Pydantic does not natively support automatic conversion of keys for extra fields,
    # so this custom method was added to handle the conversion.
    @classmethod
    def from_data(cls, **data) -> "ToolKwargs":
        # Convert camelCase keys to snake_case
        converted_data = {to_snake(k): v for k, v in data.items()}
        return cls(**converted_data)
    
    def __hash__(self):
        return hash(frozenset(self.model_dump().items()))

    def __eq__(self, other):
        if isinstance(other, ToolKwargs):
            return self.model_dump() == other.model_dump()
        return False