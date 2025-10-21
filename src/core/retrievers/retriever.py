import json
import aiohttp
import asyncio
import requests
from copy import deepcopy
from typing import Optional, Callable, Dict, Any, List, Union
from src.core.base import LamBotDocument
from langchain_core.retrievers import BaseRetriever
from tenacity import retry, stop_after_attempt, wait_exponential
from src.core.retrievers.utils import group_lambot_documents
from src.core.retrievers.utils import redact_pii
from src.models.citation import CitationTagAliasSpec

# Note: The search service is designed to retrieve fields from the index that are marked as "Retrievable" in the index schema.
# Ideally chunk_vector should not be retrievable because it is a large field and contributes to the size of the response thereby increasing the latency.

class AzureAISearchRetriever(BaseRetriever):
    """
    LangChain has its own Azure AI Search retriever class, but it makes its own decisions on how to call
    different search types and such. Here, we are using the same model where we provide search query
    REST API kwargs and possibly override the "search" field and "vectorQueries" text field.
    """

    azure_search_config: Dict[str, Any]
    index_name: str
    tool_name: str
    citation_field_mappings: Dict[str, CitationTagAliasSpec]
    search_api_key: str
    search_api_base: str
    search_api_version: str
    redact_pii: bool = True
    additional_context: Optional[Dict[str, Any]] = None
    rate_limit: int = 5
    top_k: int = 5
    formatter: Optional[Callable[[str], str]]

    @property
    def _build_search_url(self) -> str:
        return f"{self.search_api_base}/indexes/{self.index_name}/docs/search?api-version={self.search_api_version}"

    @property
    def _headers(self) -> Dict[str, str]:
        return {"Content-Type": "application/json", "api-key": self.search_api_key}

    def _prepare_payload(self, query: str) -> Dict:
        # Create a deep copy of the search config since it might have nested dictionaries
        payload = deepcopy(self.azure_search_config)
        payload.update({"top": self.top_k})
        if "search" in payload and payload["search"] is not None:
            payload["search"] = query
        if "vectorQueries" in payload:
            for vector_query in payload["vectorQueries"]:
                vector_query["text"] = query
                if "k" in vector_query:
                    vector_query["k"] = self.top_k
        
        return payload

    # Retry the function up to 4 times with exponential backoff starting at 2 seconds and capping at 6 seconds
    @retry(
        stop=stop_after_attempt(4), wait=wait_exponential(multiplier=1, min=2, max=6)
    )
    def _search(self, payload: Dict) -> List[dict]:
        search_url = self._build_search_url
        response = requests.post(
            search_url, headers=self._headers, data=json.dumps(payload)
        )
        if response.status_code != 200:
            raise requests.exceptions.HTTPError(f"Error in search request: {response}")

        return json.loads(response.content)["value"]

    # Retry the function up to 4 times with exponential backoff starting at 2 seconds and capping at 6 seconds
    @retry(
        stop=stop_after_attempt(4), wait=wait_exponential(multiplier=1, min=2, max=6)
    )
    async def _asearch(self, payload: Dict) -> List[dict]:
        search_url = self._build_search_url
        async with asyncio.Semaphore(self.rate_limit):
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    search_url, headers=self._headers, data=json.dumps(payload)
                ) as response:
                    response_json = await response.json()
                    if response.status != 200:
                        raise requests.exceptions.HTTPError(f"Error in search request: {response_json}")
        return response_json.get("value")
    
    @staticmethod
    def is_vector_field(input_list: list) -> bool:
        """
        Check if the input list is a vector field.

        Args:
            input_list (list): The list to check.

        Returns:
            bool: True if the list is a vector field, False otherwise.
        """
        if isinstance(input_list, list) and len(input_list) > 512:
            return isinstance(input_list[0], float)
        return False

    def _prepare_documents_from_response(
        self, search_response: List[dict], return_grouped_citation: bool = False
    ) -> List[Union[LamBotDocument, List[LamBotDocument]]]:
        lambot_documents = []
        for item in search_response:
            if "chunk" not in item:
                raise KeyError(
                    "Each dictionary in search_response must contain the key 'chunk'"
                )

            # Ignore the vector fields
            metadata = {
                key: value for key, value in item.items()
                if not self.is_vector_field(value)
            }

            llm_context = ""

            # Add additional context fields to the llm_context 
            if self.additional_context:
                for field_name, field_alias in self.additional_context.items():
                    value = metadata.get(field_name)
                    if value:
                        llm_context += f"{str(field_alias)}: {str(value)}" + "\n"

            # Extract the chunk from metadata
            chunk = metadata.pop("chunk")
            
            # Redact PII from the chunk. If no PII is found, the original chunk is returned.
            # Example: "Samsung has a new product" -> "Customer has a new product"
            redacted_pii_chunk = redact_pii(chunk) if self.redact_pii else chunk
            llm_context += redacted_pii_chunk

            # Create LamBotDocument object and add to the list
            lambot_document = LamBotDocument(
                page_content=self.formatter(llm_context) if self.formatter else "",
                metadata=metadata,
                llm_context=llm_context,
                origin=self.tool_name,
                citation_field_mappings=self.citation_field_mappings,
            )
            lambot_documents.append(lambot_document)
        
        if return_grouped_citation:
            return group_lambot_documents(lambot_documents)
        
        return lambot_documents

    def _get_relevant_documents(self, query: str, return_grouped_citation: bool = False) -> List[Union[LamBotDocument, List[LamBotDocument]]]:

        payload = self._prepare_payload(query)
        search_response = self._search(payload)
        lambot_documents = self._prepare_documents_from_response(search_response, return_grouped_citation)

        return lambot_documents

    async def _aget_relevant_documents(self, query: str, return_grouped_citation: bool = False) -> List[Union[LamBotDocument, List[LamBotDocument]]]:

        payload = self._prepare_payload(query)
        search_response = await self._asearch(payload)
        lambot_documents = self._prepare_documents_from_response(search_response, return_grouped_citation)

        return lambot_documents
