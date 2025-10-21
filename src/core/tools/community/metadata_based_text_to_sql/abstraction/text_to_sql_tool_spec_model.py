from src.models.base import ConfiguredBaseModel
from pydantic import BaseModel, Field
from typing import Dict, Optional, Tuple, Any


class TextToSQLRetrieverSpec(ConfiguredBaseModel):
    index_name: str = Field(..., description="Name of the index.")
    search_config: Dict[str, Any] = Field(
        ..., description="Search configuration for the tool."
    )
    use_new_search_service: Optional[bool] = Field(
        default=False, description="Use the new search service."
    )


class TextToSQLToolSpec(ConfiguredBaseModel):
    tool_name: str = Field(..., description="Name of the tool")
    description: str = Field(..., description="Description of the tool")
    schema_retriever_spec: TextToSQLRetrieverSpec = Field(
        ..., description="tool spec to spawn a schema retriever"
    )
    metadata_retriever_spec: TextToSQLRetrieverSpec = Field(
        ..., description="tool spec to spawn a metadata retriever"
    )
    sample_queries_retriever_spec: TextToSQLRetrieverSpec = Field(
        ..., description="tool spec to spawn a sample queries retriever"
    )
    prompts: Dict[str, Tuple[str, str]] = Field(..., description="Prompts for the tool.")


class SQLQuery(BaseModel):
    sql_query: str = Field(
        description="A SQL query to be executed.",
    )


class ToolInput(BaseModel):
    """Input to the tool."""

    query: str = Field(description="User question to be processed by the tool.")
