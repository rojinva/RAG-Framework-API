import os

# pydantic data models
from pydantic import Field, field_validator, model_validator, BeforeValidator, AnyUrl, EmailStr
from src.models.base import ConfiguredBaseModel
from uuid import UUID, uuid4
from typing_extensions import Annotated
from typing import List, Dict, Any, Optional
from src.models.access_conditions import AccessConditions
from datetime import datetime
from src.models.functions import datetime_now
from src.models.constants import LLMFeature, AzureOpenAIRegion
from src.models.citation import Citation
from src.models.tool import ToolArtifact
from src.models.deep_research import DeepResearchConfig

def validate_tool_config(v):
    """Convert string to ToolConfig object if needed
    This can happen when a user creates a LamBotConfig and does a POST.

    The request is sent as a list of strings, but we need to validate the rest of the fields
    are as expected.
    
    """
    if isinstance(v, str):
        return {"name": v, "display_name": v}
    return v

def validate_language_model_config(v):
    """Convert string to LanguageModelConfig object if needed
    
    This can happen when a user creates a LamBotConfig and does a POST.

    The request is sent as a list of strings, but we need to validate the rest of the fields
    are as expected.
    """
    if isinstance(v, str):
        return {"name": v, "display_name": v}
    return v

class ToolConfig(ConfiguredBaseModel):
    name: str = Field(..., description="Name of the tool.", min_length=3)
    display_name: Optional[str] = Field(None, description="Display name of the tool.", min_length=3)
    description: Optional[str] = Field(None, description="Description of the tool.")
    tool_type: Optional[str] = Field(None, description="Type of the tool.")
    discoverable: Optional[bool] = Field(None, description="Indicates if the tool config is discoverable in the wizard.")
    security_groups: Optional[List[str]] = Field(None, description="Security groups of the tool.")
    security_group_ids: Optional[List[str]] = Field(None, description="Security group ids of the tool.")
    user_has_access: Optional[bool] = Field(None, description="Indicates if the user has access to the tool. This field is not stored in MongoDB.")
    tooltip: Optional[str] = Field(None, description="Tooltip for the tool.")

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, ToolConfig):
            return self.name == other.name
        return False

class LogoFile(ConfiguredBaseModel):
    """Model for avatar file configuration supporting light and dark themes."""
    light: Optional[str] = Field(None, description="Avatar file path for light theme.")
    dark: Optional[str] = Field(None, description="Avatar file path for dark theme.")

class LanguageModelConfig(ConfiguredBaseModel):
    name: str = Field(..., description="Name of the language model.")
    deployment_name: Optional[str] = Field(None, description="Deployment name of the language model.")
    display_name: Optional[str] = Field(None, description="Display name for the app.")
    description: Optional[str] = Field(None, description="Description for the app.")
    discoverable: Optional[bool] = Field(None, description="Indicates if the config is discoverable in the wizard.")
    unsupported_features: Optional[List[LLMFeature]] = Field([], description="List of unsupported features of the LLM")
    region: Optional[AzureOpenAIRegion] = Field(None, description="Region of the language model.")
    api_version: Optional[str] = Field(None, description="API version of the language model.")
    api_key: Optional[str] = Field(None, description="API key for the language model.", exclude=True)
    endpoint: Optional[str] = Field(None, description="Endpoint of the language model.")

    @model_validator(mode="before")
    def populate(cls, values):
        values["api_version"] = os.getenv("AZURE_OPENAI_API_VERSION")
        region = values.get("region")
        api_key_name = f"AZURE_OPENAI_API_KEY_{region.upper()}"
        endpoint_name = f"AZURE_OPENAI_ENDPOINT_{region.upper()}"
        values["api_key"] = os.getenv(api_key_name)
        values["endpoint"] = os.getenv(endpoint_name)
        return values

class QueryConfig(ConfiguredBaseModel):
    system_message: Optional[str] = Field(
        None, description="System message used by this LamBot."
    )
    temperature: Optional[float] = Field(
        None, description="Temperature of the Language Model"
    )
    selected_tools: Optional[List[Annotated[ToolConfig, BeforeValidator(validate_tool_config)]]] = Field(
        None, description="Selected Tool Configs"
    )
    language_model: Optional[Annotated[LanguageModelConfig, BeforeValidator(validate_language_model_config)]] = Field(
        None, description="Language Model to use."
    )
    top_k: Optional[int] = Field(
        None, description="Number of citations to retrieve from retriever tools."
    )
    force_tool_call: Optional[bool] = Field(
        None, description="Whether to force a tool call."
    )
    deep_research: Optional[DeepResearchConfig] = Field(
        None, description="Configuration for deep research."
    )
    tool_kwargs: Optional[dict[str, dict[str, Any]]] = Field(
        None, description="Additional keyword arguments for specific tools mapped by tool name."
    )


class LamBotToolCustomize(ConfiguredBaseModel):
    """Allows a LamBot to override or customize tool behavior to be specific to the LamBot rather than the generic default settings of the tool creator"""
    name: str = Field(..., description="Name of the tool.")
    tooltip: str = Field(..., description="Tooltip for the tool.")


class LamBotConfig(ConfiguredBaseModel):
    id: UUID = Field(..., default_factory=uuid4)
    name: str = Field(..., description="Unique name for this LamBot.")
    display_name: str = Field(..., description="Display name for this LamBot.")
    description: str = Field(..., description="Short description of this LamBot.")
    creator: str = Field(..., description="Name of the creator")
    creation_date: datetime = Field(
        ..., description="Creation date of the bot.", default_factory=datetime_now
    )
    last_modified_date: datetime = Field(
        ..., description="Last modified date", default_factory=datetime_now
    )
    api_version: str = Field(..., description="API Version")
    default_query_config: QueryConfig = Field(
        ..., description="The default query config for a LamBot"
    )
    tools: List[Annotated[ToolConfig, BeforeValidator(validate_tool_config)]] = Field(
        ..., description="Tools available to be called by this LamBot."
    )
    tool_categories: Optional[Dict[str, List[str]]] = Field(None, description="Mapping of category headers to tools for advanced controls panel")
    conversation_starters: List[str] = Field(
        ..., description="List of conversation starters for this LamBot."
    )
    welcome_message: Optional[str] = Field(None, description="Welcome message for this LamBot.")
    combine_retriever_tools: bool = Field(
        ...,
        description="Whether retriever tools should be combined into a single multi-retriever tool.",
    )
    suggest_followup_questions: bool = Field(
        ..., description="Whether the LamBot will suggest follow-up questions."
    )
    supported_language_models: List[Annotated[LanguageModelConfig, BeforeValidator(validate_language_model_config)]] = Field(
        ..., description="List of supported language models."
    )
    access_conditions: AccessConditions = Field(
        ..., description="Access control policy for the LamBot."
    )
    statistics: Optional[dict] = Field(None, description="Statistics or analytics for this LamBot.")
    personal: Optional[bool] = Field(
        False, description="Whether this LamBot is a personal configuration"
    )
    ui_components: Optional[dict] = Field(None, description="UI components configuration for this LamBot.")
    sharepoint_entries: List[Any] = Field(default_factory=list, description="List of SharePoint entries for this LamBot.")
    user_has_access: Optional[bool] = Field(
        None, description="Indicates if the user has access to this LamBot. This field is not stored in MongoDB."
    )
    sharepoint_urls: Optional[List[AnyUrl]] = Field(None, description="List of SharePoint URLs the SharePoint tool can access.")
    owner: Optional[str] = Field(None, description="Owner of the LamBot.")
    audience: Optional[str] = Field(None, description="Intended audience for the LamBot.")
    tool_customize: Optional[List[LamBotToolCustomize]] = Field(None, description="Custom changes for the tool.")
    logo_file: Optional[LogoFile] = Field(None, description="Avatar file configuration for the LamBot.")

    @field_validator("default_query_config")
    def validate_default_query_config(cls, v):
        required_fields = QueryConfig().get_field_names(by_alias=False)
        missing_fields = [
            field for field in required_fields if getattr(v, field) is None
        ]
        if missing_fields:
            raise ValueError(
                f"All fields in default_query_config must be populated. Missing fields: {', '.join(missing_fields)}"
            )
        return v
    
class LamBotTransferRequest(ConfiguredBaseModel):
    new_owner: EmailStr
    addSharing: Optional[bool] = None


class AssistantMessage(ConfiguredBaseModel):

    chunk: Optional[str] = Field(default=None, description="The full textual response from the assistant.")
    citations: Optional[List[Citation]] = Field(default=None, description="List of citation objects referenced in the response.")
    followup_questions: Optional[List[str]] = Field(default=None, description="Suggested follow-up questions for the user.")
    tool_artifacts: Optional[List[ToolArtifact]] = Field(default=None, description="List of tool-related outputs or files linked to the response.")

class UserMessage(ConfiguredBaseModel):
    content: Optional[str] = Field(default=None, description="The raw message text entered by the user.")
 
class MessageConfig(ConfiguredBaseModel):

    user: Optional[UserMessage] = Field(default=None, description="The user's input message .")
    assistant: Optional[AssistantMessage] = Field(default=None, description="The assistant's response message.")
    created_at: datetime = Field(..., description="Timestamp when this message interaction occurred.")

class ConversationDocumentConfig(ConfiguredBaseModel):

    title: Optional[str] = Field(default=None, description="Title of the conversation thread.")
    thread_id: Optional[str] = Field(default=None, description="Unique identifier for the conversation thread.")
    messages: List[MessageConfig] = Field(..., description="Chronologically ordered list of message interactions.")
    lambot_id: Optional[str] = Field(default=None, description="Identifier of the LamBot model used in the conversation.")
    created_at: Optional[datetime] = Field(default=None, description="Timestamp when the conversation was started.")
    username: Optional[str] = Field(default=None, description="Email or username of the user owning this conversation.")