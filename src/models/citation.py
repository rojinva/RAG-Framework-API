from pydantic import Field, AnyUrl
from src.models.base import ConfiguredBaseModel
from src.models.constants import CitationType
from typing import List, Dict, Optional
from src.models.constants import FileExtension

class CitationTagAliasSpec(ConfiguredBaseModel):
    default: str = Field(
        ..., description="Default alias for the CitationTag display name"
    )
    file_extension_aliases: Optional[Dict[FileExtension, str]] = Field(
        None, description="File extension specific aliases for the CitationTag display name",
    )

class CitationTag(ConfiguredBaseModel):
    display_name: str = Field(
        ..., description="Display name of the CitationTag", examples=["Row", "Sheet name"]
    )
    content: str = Field(
        ...,
        description="Content of the CitationTag",
        examples=["5", "sample_sheet_name"],
    )
    is_visible: bool = Field(
        ...,
        description="Whether to display the CitationTag in the Citation",
    )


class Citation(ConfiguredBaseModel):
    origin: str = Field(..., description="Name of the tool that generated the citation")
    display_name: Optional[str] = Field(None, description="Display Name")
    display_number: int = Field(..., description="Display Number")
    type: Optional[CitationType] = Field(None, description="Type of Citation")
    url: Optional[AnyUrl] = Field(None, description="Source link of the citation")
    tags: Optional[List[CitationTag]] = Field(None, description="Citation Tags")
    is_used: bool = Field(False, description="Whether the citation was cited in text by the LamBot.")
