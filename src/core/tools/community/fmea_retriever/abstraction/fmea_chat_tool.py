import os
from typing import Dict, Type, Optional, List, Tuple
from pydantic import BaseModel
from src.core.base import LamBotDocument
from src.core.base import LamBotTool
from langchain_core.retrievers import BaseRetriever
from src.core.retrievers.retriever import AzureAISearchRetriever
from langchain_openai import AzureChatOpenAI
from src.models import ToolType
from dotenv import load_dotenv
from .fmea_chat_tool_spec_model import FMEAToolSpec, ToolInput, FMEARetrieverSpec,StaticData
from src.models.intermediate_step import IntermediateStep
import re
from ..prompts import FMEA_INSTRUCTION_PROMPT
load_dotenv(override=True)
from src.clients import LifespanClients
from src.core.database.lambot import LamBotMongoDB
from src.models.constants import LanguageModelName
from src.clients.azure import openai_token_provider

from dotenv import load_dotenv
load_dotenv()

llm_config_service = LamBotMongoDB.get_instance().language_model_config_db


class LamBotFMEAChatTool(LamBotTool):
    """FMEA Agent tool."""
    args_schema: Type[BaseModel] = ToolInput
    tool_spec: FMEAToolSpec

    def __init__(
        self,
        name: str,
        description: str,
        tool_spec: FMEAToolSpec,
        tool_type: ToolType,
    ):
        super().__init__(
            name=name, description=description, tool_type=tool_type, tool_spec=tool_spec
        )
        self.tool_spec = tool_spec

    @classmethod 
    def _get_tool_description(cls, tool_spec: FMEAToolSpec) -> str:
        """Get the tool description from the tool_description_prompt."""
        return cls._fetch_prompt(tool_spec.prompts["tool_description_prompt"])

    @classmethod
    def _fetch_prompt(cls, prompt_data: Tuple[str, str]) -> str:
        """Fetch prompt using LifespanServices."""
        prompt_name, fallback_prompt = prompt_data
        client = LifespanClients.get_instance().langfuse_manager
        return client.get_prompt(prompt_name=prompt_name, fallback_prompt=fallback_prompt)

    @classmethod
    def from_tool_spec(cls, tool_spec: FMEAToolSpec):
        name = tool_spec.tool_name
        description = cls._get_tool_description(tool_spec)
        tool_type = ToolType.non_retriever_tool
        return cls(
            name=name, description=description, tool_spec=tool_spec, tool_type=tool_type
        )

    @property
    def retrievers(self) -> List[BaseRetriever]:
        """Configure and return the AzureAISearchRetriever based on the provided tool configuration."""
        return self._configure_retrievers(self.tool_spec)

    def _configure_single_retriever(self, tool_spec: FMEARetrieverSpec) -> BaseRetriever:
        """Configure and return the AzureAISearchRetriever based on the provided tool configuration."""
        return self._create_retriever(tool_spec.index_name, tool_spec.search_config)

    def _configure_retrievers(self, tool_spec: FMEAToolSpec) -> List[BaseRetriever]:
        spec = tool_spec.historical_fmea_retriever_spec or tool_spec
        return [self._create_retriever(spec.index_name, spec.search_config)]

    def _create_retriever(self, index_name: str, search_config: Dict) -> BaseRetriever:
        """Helper method to create a retriever."""
        return AzureAISearchRetriever(
            name=index_name,
            index_name=index_name,
            tool_name=index_name,
            citation_field_mappings={},
            search_api_key=os.getenv("SEARCH_API_KEY"),
            search_api_base=os.getenv("SEARCH_API_BASE"),
            search_api_version=os.getenv("SEARCH_API_VERSION"),
            azure_search_config=search_config,
            top_k=search_config.get("top"),
            formatter=None,
            redact_pii=False,
        )

    def _escape_single_quotes(self, s: str) -> str:
        return s.replace("'", "''")

    def _build_filter_clause(self, query: str) -> str:
        ql = query.lower()
        clauses = self._extract_filter_clauses(ql)
        return " and ".join(clauses)

    def _extract_filter_clauses(self, ql: str) -> List[str]:
        """Extract filter clauses based on the query."""
        clauses = []
        rpn_match = re.search(r"rpn\s*>\s*(\d+)", ql)
        if rpn_match:
            clauses.append(f"RPN gt {rpn_match.group(1)}")
        matched_keywords = [kw for kw in StaticData.KNOWN_KEYWORDS if kw.lower() in ql]
        if matched_keywords:
            ors = [
                f"search.ismatch('{self._escape_single_quotes(kw)}', 'parent_filename') or "
                f"search.ismatch('{self._escape_single_quotes(kw)}', 'enterprise_keywords') or "
                f"search.ismatch('{self._escape_single_quotes(kw)}', 'title')"
                for kw in matched_keywords
            ]
            clauses.append(f"({' or '.join(ors)})")
        if "class" in ql:
            clauses.append("(Class eq 1 or Class eq 2)")
        return clauses

    def _build_orderby_clause(self, query: str) -> str:
        order_fields = self._extract_order_fields(query.lower())
        order_fields.append("RPN desc")
        return " , ".join(order_fields)

    def _extract_order_fields(self, ql: str) -> List[str]:
        """Extract order fields based on the query."""
        order_fields = []
        if "occurrence" in ql:
            order_fields.append("Occurrence desc")
        if any(keyword in ql for keyword in ["detection", "detectable", "detection rating"]):
            order_fields.append("Detection desc")
        if "severity" in ql:
            order_fields.append("Severity desc")
        return order_fields

    def _retrieve(self, query: ToolInput, filter_keyword: Optional[str] = None):
        retrieved_lambot_documents = []
        filter_clause = self._build_filter_clause(query.query)
        orderby_clause = self._build_orderby_clause(query.query)

        for retriever in self.retrievers:
            self._update_retriever_config(retriever, filter_clause, filter_keyword, orderby_clause, query.query)
            docs = retriever.invoke(query.query)
            retrieved_lambot_documents.extend(docs)

        return retrieved_lambot_documents

    def _update_retriever_config(self, retriever, filter_clause, filter_keyword, orderby_clause, query_text):
        """Update retriever configuration."""
        retriever.azure_search_config["filter"] = filter_clause or (
            f"search.ismatch('{filter_keyword}', 'metadata')" if filter_keyword else ""
        )
        retriever.azure_search_config["orderby"] = orderby_clause or ""
        retriever.azure_search_config["vectorQueries"] = [
            {
                "kind": "text",
                "text": query_text,
                "fields": "chunk_vector",
                "k": 15,
                "weight": 5.0,
            }
        ]
        retriever.azure_search_config["scoringProfile"] = "rpnBooast"

    @staticmethod
    def generate_output_with_llm_call(context, query=None) -> str:
        gpt5_chat_llm_config = llm_config_service.fetch_language_model(LanguageModelName.GPT_5_CHAT)
        llm = AzureChatOpenAI(
            azure_ad_token_provider=openai_token_provider,
            azure_endpoint=gpt5_chat_llm_config.endpoint,
            api_version=gpt5_chat_llm_config.api_version,
            azure_deployment=gpt5_chat_llm_config.deployment_name,
            model=gpt5_chat_llm_config.name,
            temperature=0.0,
            seed=42,
            streaming=False,
        )
        input_text = f"{context} {query}" if query else context
        return llm.invoke(input_text)

    @staticmethod
    def convert_llm_contexts_to_string(lambot_documents: List[LamBotDocument]) -> str:
        return "\n".join([document.llm_context for document in lambot_documents])

    def _create_context_hardcoded(self, prompt_type: str, list_of_strings, query=None, conversation_history=None):
        if prompt_type == "answer_generic_questions":
            prompt = FMEA_INSTRUCTION_PROMPT
        else:
            raise ValueError(f"Unknown prompt type: {prompt_type}")
        return f"{prompt}{query}{list_of_strings}{conversation_history}"

    def answer_generic_questions(self, llm_context, query, conversation_history):
        context = self._create_context_hardcoded("answer_generic_questions", llm_context, query, conversation_history)
        return self.generate_output_with_llm_call(context)

    def generic_response(self, query, conversation_history):
        lambot_documents = self._retrieve(ToolInput(query=query))
        llm_contexts = [document.llm_context for document in lambot_documents]
        return self.answer_generic_questions(llm_contexts, query, conversation_history)

    def _run(self, query: ToolInput) -> str:
        self.dispatch_intermediate_step(
            intermediate_step=IntermediateStep(message="Processing your query and getting context from FMEA Datasource, please wait…")
        )
        conversation_history = ''
        return self.generic_response(query, conversation_history)