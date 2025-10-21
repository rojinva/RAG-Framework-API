from typing import Dict, List, Optional
from pydantic.v1 import Field
from langchain_core.retrievers import BaseRetriever
from src.core.retrievers import MultiRetriever
from src.core.rerankers import SemanticReranker
from langchain_core.prompts import PromptTemplate
from src.models import ToolType, MultiRetrieverToolSpec
from .retriever_tool import LamBotRetrieverTool
from src.models.intermediate_step import IntermediateStep
from src.clients import LifespanClients
from ..retriever.multiretriever_prompts.generic import MULTIRETRIEVER_INSTRUCTION_PROMPT, MULTIRETRIEVER_TOOL_DESCRIPTION_PROMPT
from dotenv import load_dotenv
load_dotenv(override=True)


fallback_multiretriever_tool_spec = MultiRetrieverToolSpec(
    tool_name="multi_retriever",
    prompts={
        "instruction_prompt": (
            "MULTIRETRIEVER_INSTRUCTION_PROMPT",
            MULTIRETRIEVER_INSTRUCTION_PROMPT,
        ),
        "tool_description_prompt": (
            "MULTIRETRIEVER_TOOL_DESCRIPTION_PROMPT",
            MULTIRETRIEVER_TOOL_DESCRIPTION_PROMPT,
        ),
    },
)


class LamBotMultiRetrieverTool(LamBotRetrieverTool):
    """Multi-retriever tool."""

    retriever_tools: List[LamBotRetrieverTool] = Field(...)
    multi_retriever_top_k: int = Field(default=25)
    display_names: List[str] = Field(...)

    def __init__(
        self,
        tool_spec: MultiRetrieverToolSpec,
        tool_type: ToolType,
        retriever_tools: List[LamBotRetrieverTool],
        display_names: List[str],
        multi_retriever_top_k: Optional[int] = 25,
    ):
        super().__init__(
            name=tool_spec.tool_name,
            description=self._get_tool_description(tool_spec),
            tool_spec=tool_spec,
            tool_type=tool_type,
            display_names=display_names,
        )
        self.retriever_tools = retriever_tools
        self.multi_retriever_top_k = multi_retriever_top_k
        self.display_names = display_names

    @classmethod
    def from_tools(cls, retriever_tools: List[LamBotRetrieverTool], tool_spec: MultiRetrieverToolSpec, display_names: Optional[List[str]], multi_retriever_top_k: Optional[int] = 25) -> "LamBotMultiRetrieverTool":
        return cls(
            tool_spec=tool_spec,
            tool_type=ToolType.retriever_tool,
            retriever_tools=retriever_tools,
            display_names=display_names,
            multi_retriever_top_k=multi_retriever_top_k,
        )
    
    def _create_intial_tool_intermediate_step(self) -> IntermediateStep:
        """Stream back how many data sources (i.e., top-level retrievers, counting multi-retrievers as one) are being searched over."""
        num_retrievers = len(self.display_names)
        
        if num_retrievers <= 3:
            if num_retrievers == 2:
                retriever_list = f"{self.display_names[0]} and {self.display_names[1]}"
            elif num_retrievers == 3:
                retriever_list = f"{self.display_names[0]}, {self.display_names[1]}, and {self.display_names[2]}"
            else:
                retriever_list = self.display_names[0]
            message = f"Searching {retriever_list} for relevant documents..."
        else:
            message = f"Searching {num_retrievers} data sources for relevant documents..."
        
        return IntermediateStep(message=message)
    
    @classmethod
    def _get_prompt(cls, tool_spec: MultiRetrieverToolSpec, prompt_key: str) -> str:
        """
        Retrieve the prompt with double fallback logic.

        This method fetches the primary prompt specified by `prompt_key` from `MultiRetrieverToolSpec`.
        If the primary prompt is not available, it falls back to a secondary prompt specified
        by the same `prompt_key` in `fallback_multiretriever_tool_spec`.

        The fallback logic works as follows:
        1. Attempt to retrieve the primary prompt using `primary_prompt_name`.
        2. If the primary prompt is not available on Langfuse, use local `primary_fallback_prompt`.
        3. If `primary_fallback_prompt` is not available, attempt to retrieve the secondary fallback prompt from Langfuse using `secondary_fallback_prompt_name`.
        4. If the secondary fallback prompt is not available on Langfuse, use `secondary_fallback_prompt` stored locally.

        Args:
            tool_spec (MultiRetrieverToolSpec): The specification dictionary containing the primary prompt details.
            prompt_key (str): The key to access the prompt details in both `tool_spec` and `fallback_multiretriever_tool_spec`.

        Returns:
            str: The retrieved prompt.
        """
        client = LifespanClients.get_instance().langfuse_manager
        primary_prompt_name, primary_fallback_prompt = tool_spec.prompts[prompt_key]
        secondary_fallback_prompt_name, secondary_fallback_prompt = fallback_multiretriever_tool_spec.prompts[prompt_key]

        fallback_prompt = primary_fallback_prompt or client.get_prompt(
            prompt_name=secondary_fallback_prompt_name,
            fallback_prompt=secondary_fallback_prompt
        )

        prompt = client.get_prompt(
            prompt_name=primary_prompt_name,
            fallback_prompt=fallback_prompt
        )

        return prompt

    @classmethod
    def _get_tool_description(cls, tool_spec: Dict) -> str:
        """Get the tool description from the tool_description_prompt."""
        return cls._get_prompt(tool_spec, "tool_description_prompt")
    
    @property
    def instruction_prompt(self) -> PromptTemplate:
        """Get the instruction prompt with fallback."""
        return self._get_prompt(self.tool_spec, "instruction_prompt")

    @property
    def retriever(self) -> BaseRetriever:
        """Configure and return the MultiRetriever based on the provided tool configuration."""
        return self._configure_multi_retriever()

    def _configure_multi_retriever(
        self,
    ) -> BaseRetriever:
        """Configure and return the MultiRetriever based on the provided retriever tools."""
        return MultiRetriever(
            name=self.name,
            retriever_tools=self.retriever_tools,
            reranker=SemanticReranker(),
            top_k=self.multi_retriever_top_k,
        )

    def override_top_k(self, k: int):
        """Override the multi_retriever_top_k value."""

        self.multi_retriever_top_k = k
        # Also update the top_k for each individual retriever tool
        for tool in self.retriever_tools:
            if isinstance(tool, LamBotRetrieverTool):
                tool.override_top_k(k)
            else:
                raise TypeError(f"Expected instance of LamBotRetrieverTool, got {type(tool)} instead")
            
        # Reconfigure the MultiRetriever instance
        self._configure_multi_retriever()