from pydantic import BaseModel, Field
from typing import Optional

class LamBotConfigQueryParams(BaseModel):
    """
    Query parameters for LamBot configuration searches.
    This model centralizes all query parameters for the lambot-configs endpoint.
    """
    displayName: Optional[str] = Field(None, description="Filter by display name", example="Quality")
    creator: Optional[str] = Field(None, description="Filter by creator's username", example="First.Last@lamresearch.com")
    personal: Optional[bool] = Field(None, description="Filter by personal configuration", example=True)
    name: Optional[str] = Field(None, description="Filter by unique name", example="quality-assistant")

