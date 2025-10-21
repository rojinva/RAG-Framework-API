import os
import pyodbc
import asyncio
import pandas as pd

from typing import Type, Optional, List
from pydantic import BaseModel
from src.core.base import LamBotDocument
from src.core.base import LamBotTool
from langchain_core.retrievers import BaseRetriever
from langchain_core.prompts import PromptTemplate
from src.core.retrievers.retriever import AzureAISearchRetriever
from langchain_openai import AzureChatOpenAI
from src.models import ToolType
from src.models.constants import LanguageModelName
from itertools import chain
from .text_to_sql_tool_spec_model import TextToSQLToolSpec, ToolInput, SQLQuery, TextToSQLRetrieverSpec
from .explainer import TextToSQLExplainer
from dotenv import load_dotenv
from src.core.database.lambot import LamBotMongoDB
from src.clients import LifespanClients
from src.clients.azure import openai_token_provider

load_dotenv(override=True)
llm_config_service = LamBotMongoDB.get_instance().language_model_config_db

class LamBotTextToSQLTool(LamBotTool):
    """Retriever tool."""

    args_schema: Type[BaseModel] = ToolInput
    tool_spec: TextToSQLToolSpec
    explainer: Optional[TextToSQLExplainer] = None

    def __init__(
        self,
        name: str,
        description: str,
        tool_spec: TextToSQLToolSpec,
        tool_type: ToolType,
    ):
        super().__init__(
            name=name, description=description, tool_type=tool_type, tool_spec=tool_spec
        )
        self.tool_spec = tool_spec
        self.explainer = TextToSQLExplainer(tool_name=name) 

    @classmethod
    def from_tool_spec(cls, tool_spec: TextToSQLToolSpec):
        name = tool_spec.tool_name
        description = cls._get_tool_description(tool_spec)
        tool_type = ToolType.non_retriever_tool
        return cls(
            name=name, description=description, tool_spec=tool_spec, tool_type=tool_type
        )

    @classmethod
    def _get_tool_description(cls, tool_spec: TextToSQLToolSpec) -> str:
        """Get the tool description from the tool_description_prompt."""
        prompt_name, fallback_prompt = tool_spec.prompts["tool_description_prompt"]
        client = LifespanClients.get_instance().langfuse_manager
        tool_description_prompt = client.get_prompt(
            prompt_name=prompt_name,
            fallback_prompt=fallback_prompt
        )
        return tool_description_prompt

    @property
    def retrievers(self) -> List[BaseRetriever]:
        """Configure and return the AzureAISearchRetriever based on the provided tool configuration."""
        return self._configure_retrievers(self.tool_spec)

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
    def query_generation_prompt(self) -> PromptTemplate:
        """Get the instruction prompt with fallback."""
        prompt_name, fallback_prompt = self.tool_spec.prompts["query_generation_prompt"]
        client = LifespanClients.get_instance().langfuse_manager
        query_generation_prompt = client.get_prompt(
            prompt_name=prompt_name,
            fallback_prompt=fallback_prompt
        )
        return query_generation_prompt

    def _configure_single_retriever(self, tool_spec: TextToSQLRetrieverSpec) -> BaseRetriever:
        """Configure and return the AzureAISearchRetriever based on the provided tool configuration."""
        azure_search_config = tool_spec.search_config
        
        return AzureAISearchRetriever(
            name=tool_spec.index_name,
            index_name=tool_spec.index_name,
            tool_name=tool_spec.index_name,
            citation_field_mappings={},
            search_api_key=os.getenv("SEARCH_API_KEY"),
            search_api_base=os.getenv("SEARCH_API_BASE"),
            search_api_version=os.getenv("SEARCH_API_VERSION"),
            azure_search_config=azure_search_config,
            top_k=azure_search_config.get("top"),
            formatter=None,
        )

    def _configure_retrievers(self, tool_spec: TextToSQLToolSpec) -> BaseRetriever:
        """Configure and return each of the retrievers"""
        schema_retriever = self._configure_single_retriever(
            tool_spec=tool_spec.schema_retriever_spec
        )
        metadata_retriever = self._configure_single_retriever(
            tool_spec=tool_spec.metadata_retriever_spec
        )
        sample_queries_retriever = self._configure_single_retriever(
            tool_spec=tool_spec.sample_queries_retriever_spec
        )
        return [schema_retriever, metadata_retriever, sample_queries_retriever]

    def _retrieve(self, query: ToolInput):
        """Retrieve documents based on the query synchronously."""

        retrieved_lambot_documents = []
        for retriever in self.retrievers:
            _retrieved_lambot_documents = retriever.invoke(query)
            retrieved_lambot_documents.extend(_retrieved_lambot_documents)
        return retrieved_lambot_documents

    async def _retrieve_async(self, query: ToolInput):
        """Retrieve documents based on the query asynchronously."""
        tasks = [retriever.ainvoke(query) for retriever in self.retrievers]
        _retrieved_lambot_documents = await asyncio.gather(*tasks)
        return list(chain.from_iterable(_retrieved_lambot_documents))

    @staticmethod
    def generate_query_with_llm_call(query, context) -> None:
        gpt4o_llm_config = llm_config_service.fetch_language_model(LanguageModelName.GPT_4O)
        llm = AzureChatOpenAI(
            azure_ad_token_provider=openai_token_provider,
            azure_endpoint=gpt4o_llm_config.endpoint,
            api_version=gpt4o_llm_config.api_version,
            azure_deployment=gpt4o_llm_config.deployment_name,
            model=gpt4o_llm_config.name,
            temperature=0.0,
            seed=42,
            streaming=False,
        )
        llm_structured_ouput = llm.with_structured_output(SQLQuery)
        response = llm_structured_ouput.invoke(f"{context} {query}")
        return response.sql_query

    @staticmethod
    def execute_query_in_synapse(llm_generated_query):
        
        server = os.getenv("OPENAI_SYNAPSE_READER_SERVER")
        database = os.getenv("OPENAI_SYNAPSE_READER_DATABASE")
        username = os.getenv("OPENAI_SYNAPSE_READER_USERNAME")
        password = os.getenv("OPENAI_SYNAPSE_READER_SECRET")

        # Connection string
        connection_string = f"""
            DRIVER={{ODBC Driver 17 for SQL Server}};
            SERVER={server};
            DATABASE={database};
            UID={username};
            PWD={password};
            Authentication=ActiveDirectoryPassword;
        """

        # Establishing the connection
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()
        results = None
        columns = None

        try:
            # Executing the LLM-generated query
            cursor.execute(llm_generated_query)
        
            columns = [column[0] for column in cursor.description]

            # Fetching the results
            results = cursor.fetchall()
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # Close the connection
            cursor.close()
            connection.close()
            
        return results, columns
    
    @staticmethod
    def create_dataframe(query_results, columns):
        result_dict = {column: [] for column in columns}
    
        # Iterate over each tuple
        for row in query_results:
            
            tuple_row = tuple(row)
            # Iterate over each column and corresponding value in the tuple
            for column, value in zip(columns, tuple_row):
                result_dict[column].append(value)
        
        df = pd.DataFrame(result_dict)
        return df

    @staticmethod
    def convert_llm_contexts_to_string(lambot_documents: List[LamBotDocument]) -> str:
        # @TODO: Add converting each llm_context to strings and then return the following statement.
        return "\n".join(document.llm_context for document in lambot_documents)

    def _create_context(self, lambot_documents):
        """Create context from retrieved documents."""
        RETRIEVED_CITATIONS = self.convert_llm_contexts_to_string(lambot_documents)
        self.explainer.results.context = RETRIEVED_CITATIONS
        context = self.query_generation_prompt + RETRIEVED_CITATIONS
        return context

    def _run_text_to_sql_workflow_from_documents(self, query, documents):
        context = self._create_context(documents)
        llm_generated_sql_query = self.generate_query_with_llm_call(
            query=query, context=context
        )
        self.explainer.results.user_question = query
        self.explainer.results.llm_generated_query = llm_generated_sql_query
        
        query_results, columns = self.execute_query_in_synapse(
            llm_generated_query=llm_generated_sql_query
        )
        if isinstance(query_results, list) and len(query_results)>0: 
            dataframe = self.create_dataframe(query_results, columns)
            blob_url = self.upload_dataframe_to_adls(dataframe=dataframe)
            sample_size = 10
            sample_data = dataframe.head(sample_size)
            
            self.explainer.results.query_executed = True
            self.explainer.results.query_results_df_sample = sample_data
            self.explainer.results.query_results_blob_url = blob_url
            
            if len(query_results) > sample_size:
                
                query_results = f"The data has {dataframe.shape[0]} rows, which is too large to process. Here's a sample of the data: {sample_data.to_dict(orient='list')}"
                  
        else:       
            query_results = "The generated query could not yeild any results. Please ask a different question."
            
        return query_results
    
    def explain(self):
        if self.explainer.results.query_executed:
            self.dispatch_tool_artifact(tool_artifact=self.explainer.query_display_tool_artifact)
        
            self.dispatch_tool_artifact(tool_artifact=self.explainer.query_explain_tool_artifact)
            self.dispatch_tool_artifact(tool_artifact=self.explainer.query_results_display_tool_artifact)
        else:
            self.dispatch_tool_artifact(tool_artifact=self.explainer.query_remedies_tool_artifact)
            
        self.explainer = TextToSQLExplainer(tool_name=self.name)
        

    def _run(self, query: ToolInput) -> str:
        """Run the retriever tool synchronously."""
        lambot_documents = self._retrieve(query)
        summarized_results = self._run_text_to_sql_workflow_from_documents(
            query, lambot_documents
        )
        tool_output = f"{self.instruction_prompt} {str(self.explainer.results.query_remedies)} {str(summarized_results)}"
        self.explain()
        return tool_output

    async def _arun(self, query: ToolInput) -> str:
        """Run the retriever tool asynchronously."""
        lambot_documents = await self._retrieve_async(query)
        summarized_results = self._run_text_to_sql_workflow_from_documents(
            query, lambot_documents
        )
        tool_output = f"{self.instruction_prompt} {str(self.explainer.results.query_remedies)} {str(summarized_results)}"
        self.explain()
        return tool_output