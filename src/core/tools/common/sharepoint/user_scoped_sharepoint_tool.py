import os
import aiohttp
import asyncio
from typing import Type, Dict, Any
from pydantic import BaseModel
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv(override=True)

from src.core.base import LamBotTool
from src.models.constants import ToolType
from src.models.intermediate_step import IntermediateStep
from src.core.context.vars import access_token_var
from src.models.sharepoint_tool import SharePointInput, SharePointToolSpec
from src.core.tools.common.sharepoint.utils import format_sharepoint_results

# Set up logger for this module
import logging

logger = logging.getLogger(__name__)


class UserScopedSharePointTool(LamBotTool):
    """SharePoint tool scoped to SharePoint sites and documents that the user making a request has access to."""

    args_schema: Type[BaseModel] = SharePointInput
    tool_spec: SharePointToolSpec
    copilot_search_url: str = "https://graph.microsoft.com/beta/copilot/retrieval"

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
            name=name, description=description, tool_spec=tool_spec, tool_type=tool_type
        )

    @classmethod
    def _get_tool_description(cls, tool_spec: SharePointToolSpec) -> str:
        """Get the tool description from the tool_description_prompt."""
        prompt_name, fallback_prompt = tool_spec.prompts["tool_description_prompt"]
        tool_description_prompt = cls._get_prompt(
            prompt_name=prompt_name, 
            fallback_prompt=fallback_prompt,
            label=os.getenv("LANGFUSE_LABEL", "dev")
        )
        return tool_description_prompt

    @property
    def instruction_prompt(self) -> str:
        """Get the instruction prompt for SharePoint search results."""
        prompt_name, fallback_prompt = self.tool_spec.prompts["instruction_prompt"]
        instruction_prompt = self._get_prompt(
            prompt_name=prompt_name, 
            fallback_prompt=fallback_prompt,
            label=os.getenv("LANGFUSE_LABEL", "dev")
        )
        return instruction_prompt

    def _get_headers(self) -> Dict[str, str]:
        """Get the headers including access token for the API request."""
        try:
            access_token = access_token_var.get()
            if not access_token:
                raise ValueError("No access token found in context")

            return {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }
        except Exception as e:
            logger.error(f"Failed to get access token: {e}")
            raise ValueError("Authentication required: No valid access token available")

    def _prepare_request_payload(self, query_input: SharePointInput) -> Dict[str, Any]:
        """Prepare the request payload for Microsoft Graph Copilot API."""
        payload = {
            "queryString": query_input.query,
            "dataSource": "sharePoint",
            "maximumNumberOfResults": self.tool_spec.maximum_number_of_results,
            "resourceMetadata": ["title", "author"],
        }

        return payload

    # Retry the function up to 4 times with exponential backoff starting at 2 seconds and capping at 6 seconds
    @retry(
        stop=stop_after_attempt(4), wait=wait_exponential(multiplier=1, min=2, max=6)
    )
    async def _make_api_request(
        self, payload: Dict[str, Any], headers: Dict[str, str]
    ) -> Dict[str, Any]:
        """Make the API request to Microsoft Graph Copilot endpoint."""
        async with aiohttp.ClientSession() as session:
            try:
                logger.info(
                    f"Making request to SharePoint Copilot API with query: {payload['queryString'][:100]}..."
                )

                async with session.post(
                    self.copilot_search_url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:

                    if response.status == 200:
                        result = await response.json()
                        logger.info("Successfully retrieved SharePoint results")
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(
                            f"SharePoint API request failed with status {response.status}: {error_text}"
                        )
                        raise RuntimeError(
                            f"SharePoint API request failed: {response.status} - {error_text}"
                        )

            except asyncio.TimeoutError:
                logger.error("SharePoint API request timed out")
                raise TimeoutError("SharePoint API request timed out after 30 seconds")
            except Exception as e:
                logger.error(f"Error making SharePoint API request: {e}")
                raise RuntimeError(f"Failed to query SharePoint: {str(e)}")

    def _format_results_and_dispatch_citations(self, api_response: Dict[str, Any]) -> str:
        """Format the API response and dispatch all citations at once."""
        formatted_results = format_sharepoint_results(api_response)

        return formatted_results

    def _run(self, query: str) -> str:
        """Run the SharePoint search synchronously."""
        query_input = SharePointInput(query=query)

        # Use asyncio.run to handle async call in sync context
        return asyncio.run(self._retrieve_async(query_input))

    async def _arun(self, query: str) -> str:
        """Run the SharePoint search asynchronously."""
        query_input = SharePointInput(query=query)

        return await self._retrieve_async(query_input)

    async def _retrieve_async(self, query_input: SharePointInput) -> str:
        """Retrieve documents based on the query asynchronously."""
        try:
            # Dispatch initial intermediate step
            initial_step = IntermediateStep(
                message=f'Searching SharePoint for \"{query_input.query}\"'
            )
            self.dispatch_intermediate_step(initial_step)

            # Prepare request
            payload = self._prepare_request_payload(query_input)
            headers = self._get_headers()

            # Make API request
            api_response = await self._make_api_request(payload, headers)

            # Process results
            retrieval_hits = api_response.get("retrievalHits", [])
            results_count = len(retrieval_hits)
            results_step = IntermediateStep(
                message=f"Found {results_count} SharePoint documents..."
            )
            self.dispatch_intermediate_step(results_step)

            # Format results and dispatch citations
            formatted_results = self._format_results_and_dispatch_citations(api_response)

            # Return formatted output with instruction prompt
            return self.instruction_prompt + formatted_results

        except Exception as e:
            logger.error(f"SharePoint tool execution failed: {e}")
            error_message = f"SharePoint search failed: {str(e)}"

            return f"Error: {error_message}"
