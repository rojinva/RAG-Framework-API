from enum import StrEnum
from pydantic import BaseModel, Field
from typing import Dict, Optional, Tuple, Any
from src.models.base_tool_spec import BaseToolSpec
from src.models.base import ConfiguredBaseModel
from src.models.citation import CitationTagAliasSpec

class AccessControlParam(StrEnum):
    USERNAME = "onPremisesSamAccountName"
    EMAIL = "email"
    ACCESS_TOKEN = "accessToken"


class RetrieverInput(BaseModel):
    """Input to the retriever."""

    query: str = Field(
        description="The search query string that will be sent to the retriever tool for information retrieval. This query is used to look up relevant chunks within the retriever index."
    )


class AccessControl(ConfiguredBaseModel):
    function: Any = Field(..., description="The function to get access types")
    param: AccessControlParam = Field(
        ..., description="The parameter type for the access control function"
    )
    filter_field: str = Field(
        ..., description="The field in the search service to be filtered"
    )


class RetrieverToolSpec(BaseToolSpec):
    index_name: str = Field(..., description="Name of the index.")
    redact_pii: bool = Field(
        default=True, description="Flag to indicate if PII should be redacted in the tool response."
    )
    search_config: Dict[str, Any] = Field(
        ..., description="Search configuration for the tool."
    )
    citation_field_mappings: Optional[Dict[str, CitationTagAliasSpec]] = Field(
        default_factory=dict, description="The field mappings for the citation. The key is the field name in the search service index, and the value is the alias spec."
    )
    access_control: Optional[AccessControl] = Field(
        default=None, description="Access control configuration."
    )
    formatter: Optional[Any] = Field(
        default=None, description="Optional formatter for the tool."
    )

class MultiRetrieverToolSpec(BaseModel):
    tool_name: str = Field(..., description="Name of the tool.")
    prompts: Dict[str, Tuple[str, Optional[str]]] = Field(..., description="Prompts for the tool.")