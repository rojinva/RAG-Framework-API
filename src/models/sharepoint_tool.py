from pydantic import BaseModel, Field
from src.models.base_tool_spec import BaseToolSpec


class SharePointInput(BaseModel):
    """Input schema for SharePoint Copilot API tool."""

    query: str = Field(
        description="The search query used to retrieve relevant SharePoint text extracts. Should be a single sentence with context-rich keywords.",
        max_length=1500,
    )


class SharePointToolSpec(BaseToolSpec):
    """SharePoint tool specification model."""

    maximum_number_of_results: int = Field(
        default=10,
        description="Maximum number of SharePoint results to return from Copilot API.",
    )
