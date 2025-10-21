import os
from copy import deepcopy
from typing import List, Type, Optional, Union
from pydantic import BaseModel, Field
from src.core.base import LamBotTool
from langchain_core.retrievers import BaseRetriever
from langchain_core.prompts import PromptTemplate
from src.core.retrievers.retriever import AzureAISearchRetriever
from src.models import ToolType
from src.models.retriever_tool import RetrieverInput
from src.models.intermediate_step import IntermediateStep
from src.core.context.vars import access_token_var
from src.core.utils.auth_helpers import get_user_info
from src.clients import LifespanClients
from src.models.retriever_tool import AccessControlParam, AccessControl, RetrieverToolSpec, MultiRetrieverToolSpec
from src.core.retrievers.utils import create_llm_context_string
from src.core.tools.common.retriever.utils import build_search_filter_from_filterable_fields, merge_search_filters

from dotenv import load_dotenv
load_dotenv(override=True)


class LamBotRetrieverTool(LamBotTool):
    """Retriever tool."""
    args_schema: Type[BaseModel] = RetrieverInput
    tool_spec: Union[RetrieverToolSpec, MultiRetrieverToolSpec]
    access_control_intermediate_step: IntermediateStep = Field(default=None)
    display_names: List[str] = Field(default=None)

    def __init__(self, name: str, description: str, tool_spec: RetrieverToolSpec, tool_type: ToolType, display_names: Optional[List[str]] = None):
        super().__init__(name=name, description=description, tool_type=tool_type, tool_spec=tool_spec)
        self.tool_spec = tool_spec
        self.display_names = display_names
        self.access_control_intermediate_step = None

    @classmethod
    def from_tool_spec(cls, tool_spec: RetrieverToolSpec):
        name = tool_spec.tool_name
        description = cls._get_tool_description(tool_spec)
        tool_type = ToolType.retriever_tool
        return cls(name=name, description=description, tool_spec=tool_spec, tool_type=tool_type)

    @classmethod
    def _get_tool_description(cls, tool_spec: RetrieverToolSpec) -> str:
        """Get the tool description from the tool_description_prompt."""
        prompt_name, fallback_prompt = tool_spec.prompts["tool_description_prompt"]
        client = LifespanClients.get_instance().langfuse_manager
        tool_description_prompt = client.get_prompt(
            prompt_name=prompt_name,
            fallback_prompt=fallback_prompt
        ) 
        return tool_description_prompt

    @property
    def retriever(self) -> BaseRetriever:
        """Configure and return the AzureAISearchRetriever based on the provided tool configuration."""
        return self._configure_retriever(self.tool_spec)

    @property
    def instruction_prompt(self) -> PromptTemplate:
        """Get the instruction prompt with fallback."""
        prompt_name, fallback_prompt = self.tool_spec.prompts["instruction_prompt"]
        client = LifespanClients.get_instance().langfuse_manager
        instruction_prompt = client.get_prompt(
            prompt_name=prompt_name,
            fallback_prompt=fallback_prompt
        ) 
        return instruction_prompt

    @property
    def top_k(self) -> int:
        """Get the top_k value."""
        return self.tool_spec.search_config["top"]

    def override_top_k(self, k: int):
        """Override the top_k value in the search config."""
        self.tool_spec.search_config["top"] = k

    @property
    def access_control(self) -> Optional[AccessControl]:
        """Get the access control configuration from the tool specification."""
        return self.tool_spec.access_control

    def _build_search_filter_from_tool_kwargs(self) -> Optional[str]: 
        """Builds a search filter string from tool_kwargs.filterable_fields if present."""
        filterable_fields = self.get_tool_kwarg("filterable_fields")
        if not filterable_fields:
            return None
        search_filter = build_search_filter_from_filterable_fields(filterable_fields)
        return search_filter or None

    def _configure_retriever(self, tool_spec: RetrieverToolSpec) -> BaseRetriever:
        """Configure and return the AzureAISearchRetriever based on the provided tool configuration."""
        azure_search_config = deepcopy(tool_spec.search_config)
        
        # Apply the search filter from tool keyword arguments
        original_filter = azure_search_config.get("filter")
        filter_from_tool_kwargs = self._build_search_filter_from_tool_kwargs()
        merged_filter = merge_search_filters([original_filter, filter_from_tool_kwargs])
        if merged_filter:
            azure_search_config["filter"] = merged_filter

        if self.access_control:
            # Get user information
            access_token = access_token_var.get()
            user_info = get_user_info(access_token)
            
            # Determine the parameter to pass to the access control function
            access_control_param = self.access_control.param
            param_value = user_info.get(access_control_param.value)
            if access_control_param == AccessControlParam.USERNAME:
                param_value = param_value.lower()
            
            if not param_value:
                raise ValueError(f"Invalid access control parameter specified: {access_control_param}")
            
            # Get the access types using the access control function
            access_control_function = self.access_control.function
            access_types = access_control_function(param_value)
            
            # Check if access_types is a list
            if not isinstance(access_types, list):
                raise ValueError("The access control function must return a list of strings.")
            
            # Update the search configuration with the filter conditions
            filter_field = self.access_control.filter_field
            if len(access_types) == 0:
                filter_conditions = f"{filter_field} eq '__non_existent_value__'"
            else:
                filter_conditions = f"search.in({filter_field}, '{','.join(access_types)}', ',')"

            if access_types and len(access_types) < 10:
                self.access_control_intermediate_step = IntermediateStep(
                    message=f"Filtered results to {', '.join(access_types)}"
                )

            # Combine with any existing filter in the search configuration
            # e.g., when both access control and tool_spec specify filters
            existing_filter = azure_search_config.get("filter")
            _filter = merge_search_filters([existing_filter, filter_conditions])
            if _filter:
                azure_search_config["filter"] = _filter

        return AzureAISearchRetriever(
            name=tool_spec.tool_name,
            index_name=tool_spec.index_name,
            tool_name=tool_spec.tool_name,
            redact_pii=tool_spec.redact_pii,
            additional_context=tool_spec.additional_context,
            citation_field_mappings=tool_spec.citation_field_mappings,
            search_api_key=os.getenv("SEARCH_API_KEY"),
            search_api_base=os.getenv("SEARCH_API_BASE"),
            search_api_version=os.getenv("SEARCH_API_VERSION"),
            azure_search_config=azure_search_config,
            top_k=azure_search_config.get("top"),
            formatter=tool_spec.formatter
        )
    
    def _create_intial_tool_intermediate_step(self) -> IntermediateStep:
        """Stream back how many data sources (i.e., top-level retrievers, counting multi-retrievers as one) are being searched over."""
        return IntermediateStep(
            message=f"Searching {self.display_names[0]} data source for relevant documents..."
        )

    def _retrieve(self, query: RetrieverInput):
        """Retrieve documents based on the query synchronously."""
        grouped_lambot_documents = self.retriever.invoke(query, return_grouped_citation=True)

        num_documents = sum(
            len(group) if isinstance(group, list) else 1
            for group in grouped_lambot_documents
        )
        intermediate_step_message = IntermediateStep(
            message=f"Found {num_documents} relevant documents..."
        )
        self.dispatch_intermediate_step(intermediate_step_message)

        return grouped_lambot_documents

    async def _retrieve_async(self, query: RetrieverInput):
        """Retrieve documents based on the query asynchronously."""
        grouped_lambot_documents = await self.retriever.ainvoke(query, return_grouped_citation=True)

        num_documents = sum(
            len(group) if isinstance(group, list) else 1
            for group in grouped_lambot_documents
        )
        intermediate_step_message = IntermediateStep(
            message=f"Found {num_documents} relevant documents..."
        )
        self.dispatch_intermediate_step(intermediate_step_message)

        return grouped_lambot_documents

    def _create_context(self, grouped_lambot_documents):
        """Create context from retrieved documents."""
        RETRIEVED_CITATIONS = create_llm_context_string(grouped_lambot_documents)
        context = self.instruction_prompt + "\n" + RETRIEVED_CITATIONS
        return context

    def _run(
        self, query: RetrieverInput
    ) -> str:
        """Run the retriever tool synchronously."""
        intial_tool_intermediate_step = self._create_intial_tool_intermediate_step()
        self.dispatch_intermediate_step(intial_tool_intermediate_step)

        grouped_lambot_documents = self._retrieve(query)

        if self.access_control_intermediate_step:
            self.dispatch_intermediate_step(self.access_control_intermediate_step)
        
        return self._create_context(grouped_lambot_documents)

    async def _arun(
        self,
        query: RetrieverInput
    ) -> str:
        """Run the retriever tool asynchronously."""
        intial_tool_intermediate_step = self._create_intial_tool_intermediate_step()
        self.dispatch_intermediate_step(intial_tool_intermediate_step)

        grouped_lambot_documents = await self._retrieve_async(query)

        if self.access_control_intermediate_step:
            self.dispatch_intermediate_step(self.access_control_intermediate_step)
        
        return self._create_context(grouped_lambot_documents)
    
    def __eq__(self, other):
        if isinstance(other, LamBotRetrieverTool):
            return (
                self.name == other.name and
                self.tool_spec.additional_context == other.tool_spec.additional_context and
                self._tool_kwargs == other._tool_kwargs
            )
        return False
    
    def __hash__(self):
        return hash(self.name)
    
    def set_display_names(self, display_names: List[str]):
        """Set the display names for the intermediate step."""
        self.display_names = display_names