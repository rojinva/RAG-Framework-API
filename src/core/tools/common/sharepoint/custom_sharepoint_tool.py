from src.core.tools.common.sharepoint.user_scoped_sharepoint_tool import (
    UserScopedSharePointTool,
)
from src.core.tools.common.sharepoint.utils import format_sharepoint_filter_expression
from pydantic import Field, AnyUrl
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv(override=True)
from src.models.constants import ToolType
from src.models.sharepoint_tool import SharePointInput, SharePointToolSpec


# Set up logger for this module
import logging

logger = logging.getLogger(__name__)


class CustomSharePointTool(UserScopedSharePointTool):
    """Custom SharePoint tool with specific functionality."""

    sharepoint_urls: Optional[List[AnyUrl]] = Field(default_factory=list, description="List of SharePoint URLs this tool can access")

    def __init__(
        self,
        name: str,
        description: str,
        tool_spec: SharePointToolSpec,
        tool_type: ToolType,
    ):
        super().__init__(
            name=name, description=description, tool_type=tool_type, tool_spec=tool_spec
        )
        self.tool_spec = tool_spec

    @classmethod
    def from_tool_spec(cls, tool_spec: SharePointToolSpec):
        """Create SharePointTool from a tool specification."""
        name = tool_spec.tool_name
        description = cls._get_tool_description(tool_spec)
        tool_type = ToolType.non_retriever_tool
        return cls(
            name=name, 
            description=description, 
            tool_spec=tool_spec, 
            tool_type=tool_type
        )

    def _prepare_request_payload(self, query_input: SharePointInput) -> Dict[str, Any]:
        """Prepare the request payload for Microsoft Graph Copilot API."""

        # Validate that SharePoint URLs are configured
        if not self.sharepoint_urls:
            raise ValueError("No SharePoint URLs configured for this tool. Please configure sharepoint_urls in the LamBot configuration.")

        payload = {
            "queryString": query_input.query,
            "dataSource": "sharePoint",
            "maximumNumberOfResults": self.tool_spec.maximum_number_of_results,
            "resourceMetadata": ["title", "author"],
            "filterExpression": format_sharepoint_filter_expression(self.sharepoint_urls),
        }
        
        return payload
