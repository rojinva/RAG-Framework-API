from src.models.base import ConfiguredBaseModel
from pydantic import BaseModel, Field
from typing import Dict, Optional, Tuple, Any


class FMEARetrieverSpec(ConfiguredBaseModel):
    index_name: str = Field(..., description="Name of the index.")
    search_config: Dict[str, Any] = Field(
        ..., description="Search configuration for the tool."
    )
    use_new_search_service: Optional[bool] = Field(
        default=False, description="Use the new search service."
    )


class FMEAToolSpec(ConfiguredBaseModel):
    tool_name: str = Field(..., description="Name of the tool")
    description: str = Field(..., description="Description of the tool")
    historical_fmea_retriever_spec: FMEARetrieverSpec = Field(
        ..., description="tool spec to spawn a schema retriever"
    )
    escalation_solver_fmea_retriever_spec: Optional[FMEARetrieverSpec] = Field(
        None, description="tool spec to spawn a schema retriever"
    )
    nce_fmea_retriever_spec: Optional[FMEARetrieverSpec] = Field(
        None, description="tool spec to spawn a schema retriever"
    )
    prompts: Dict[str, Tuple[str, str]] = Field(..., description="Prompts for the tool.")


class ToolInput(BaseModel):
    """Input to the tool."""

    query: str = Field(description="User question to be processed by the tool.")