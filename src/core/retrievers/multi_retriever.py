import asyncio
import warnings
from typing import List, Optional
from copy import deepcopy
from src.core.base import LamBotDocument
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents.compressor import BaseDocumentCompressor
from itertools import chain
from src.core.retrievers.utils import group_lambot_documents
from src.core.base import LamBotTool
from src.core.tools.common.retriever.utils import merge_search_filters

class MultiRetriever(BaseRetriever):

    retrievers: Optional[List[BaseRetriever]] = None
    retriever_tools: List[LamBotTool]
    reranker: BaseDocumentCompressor
    top_k: int

    def _retrieve_documents_sync(self, query) -> List[LamBotDocument]:
        retrieved_lambot_documents = []
        for retriever in self.retrievers:
            _retrieved_lambot_documents = retriever.invoke(query, return_grouped_citation=False)
            retrieved_lambot_documents.extend(_retrieved_lambot_documents)
        return retrieved_lambot_documents

    async def _retrieve_documents_async(self, query) -> List[LamBotDocument]:
        tasks = [retriever.ainvoke(query, return_grouped_citation=False) for retriever in self.retrievers]
        _retrieved_lambot_documents = await asyncio.gather(*tasks)
        return list(chain.from_iterable(_retrieved_lambot_documents))

    def _get_relevant_documents(self, query: str) -> List[LamBotDocument]:
        self._merge_retrievers_by_index_name()
        retrieved_lambot_documents = self._retrieve_documents_sync(query)
        if len(retrieved_lambot_documents) < self.top_k:
            warnings.warn(
                "The retrieved documents are less than the top k defined. Please adjust the retrievals for the retrievers."
            )

        reranked_lambot_documents = self.reranker.compress_documents(
            documents=retrieved_lambot_documents,
        )
        top_k_reranked_lambot_documents = reranked_lambot_documents[: self.top_k]
        top_k_reranked_grouped_lambot_documents = group_lambot_documents(top_k_reranked_lambot_documents)
        return top_k_reranked_grouped_lambot_documents

    async def _aget_relevant_documents(self, query: str) -> List[LamBotDocument]:
        self._merge_retrievers_by_index_name()
        retrieved_lambot_documents = await self._retrieve_documents_async(query)

        if len(retrieved_lambot_documents) < self.top_k:
            warnings.warn(
                "The retrieved documents are less than the top k defined. Please adjust the retrievals for the retrievers."
            )

        reranked_lambot_documents = self.reranker.compress_documents(
            documents=retrieved_lambot_documents,
        )
        top_k_reranked_lambot_documents = reranked_lambot_documents[: self.top_k]
        top_k_reranked_grouped_lambot_documents = group_lambot_documents(top_k_reranked_lambot_documents)
        return top_k_reranked_grouped_lambot_documents

    def _merge_retrievers_by_index_name(self) -> None:
        """Merge retrievers with the same index name by combining their filters using 'or' logic."""
        unique_index_names = list({tool.tool_spec.index_name for tool in self.retriever_tools})
        tools_with_same_index_names = []
        for index_name in unique_index_names:
            tools_with_name = [tool for tool in self.retriever_tools if tool.tool_spec.index_name == index_name]
            base_tool = deepcopy(tools_with_name[0])
            if len(tools_with_name) > 1:
                for other_tool in tools_with_name[1:]:
                    # Check if both tools have the same additional context and tool keyword arguments
                    if (
                        base_tool.tool_spec.additional_context != other_tool.tool_spec.additional_context or
                        base_tool.get_tool_kwargs() != other_tool.get_tool_kwargs()
                    ):
                        tools_with_same_index_names.append(other_tool)
                        # get out of the loop to avoid merging this tool
                        continue
                    # Merge filters with 'or' logic
                    base_filter = base_tool.tool_spec.search_config.get("filter", "")
                    other_filter = other_tool.tool_spec.search_config.get("filter", "")
                    merged_filter = merge_search_filters([base_filter, other_filter], "or")
                    # Update the base tool's search_config
                    base_tool.tool_spec.search_config["filter"] = merged_filter
                # Override the retriever tool name to reflect the merged index
                base_tool.tool_spec.tool_name = f"{index_name}_merged_retriever"
            tools_with_same_index_names.append(base_tool)

        self.retrievers = [tool.retriever for tool in tools_with_same_index_names]
