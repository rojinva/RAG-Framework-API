from typing import Dict, Optional, Tuple, Any
from pydantic import BaseModel, Field

from src.models.base import ConfiguredBaseModel
from src.models.citation import CitationTagAliasSpec

# Optional: type aliases improve readability and help reduce repetition
PromptsType = Dict[str, Tuple[str, str]]
SearchConfigType = Dict[str, Any]
CitationMappingsType = Dict[str, CitationTagAliasSpec]

class CommonSpecFields(ConfiguredBaseModel):
    """Common fields shared by both retriever and tool specifications."""
    tool_name: str = Field(..., description="Name of the tool.")
    index_name: str = Field(..., description="Name of the index.")
    prompts: PromptsType = Field(..., description="Prompts for the tool.")
    search_config: SearchConfigType = Field(..., description="Search configuration for the tool.")
    citation_field_mappings: Optional[CitationMappingsType] = Field(
        default_factory=dict,
        description="The field mappings for the citation. The key is the field name in the search service index, and the value is the alias spec.",
    )
    use_new_search_service: Optional[bool] = Field(
        default=False, description="Use the new search service."
    )
    formatter: Optional[Any] = Field(
        default=None, description="Optional formatter for the tool."
    )

class BaseRetrieverSpec(CommonSpecFields):
    """Base class for retriever specifications."""
    # No extra fields; inherits all from CommonSpecFields
    pass

class FMEARetrieverSpec(BaseRetrieverSpec):
    """FMEA-specific retriever specifications."""
    pass

class BaseToolSpec(CommonSpecFields):
    """Base class for tool specifications."""
    description: str = Field(..., description="Description of the tool")

class FMEAToolSpec(BaseToolSpec):
    """FMEA-specific tool specifications."""
    historical_fmea_retriever_spec: Optional[FMEARetrieverSpec] = None

class ToolInput(BaseModel):
    """Input to the tool."""
    query: str = Field(description="User question to be processed by the tool.")

class StaticData:
    KNOWN_KEYWORDS = [
        "O-RING", "Power Box", "Valve", "Shower Head", "PB", "PowerBox"
    ]