from pydantic import Field
from typing import Any, Dict, Optional, Tuple
from src.models.base import ConfiguredBaseModel

class BaseToolSpec(ConfiguredBaseModel):
    tool_name: str = Field(..., description="Name of the tool.")
    prompts: Dict[str, Tuple[str, str]] = Field(..., description="Prompts for the tool.")
    system_message_hint: Optional[str] = Field(
        default=None, description="Optional system message hint for the tool."
    )
    additional_context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional additional context for the tool. Example: {'author_name': 'Author Name'} where the key is the native field and the value is the alias.",
    )
    