import pandas as pd
from langchain_openai import AzureChatOpenAI
from src.models.tool import ToolArtifact
from src.models.constants import LanguageModelName
from src.core.database.lambot import LamBotMongoDB
from pydantic import BaseModel
from src.clients.azure import openai_token_provider

llm_config_service = LamBotMongoDB.get_instance().language_model_config_db


class Results(BaseModel):
    user_question: str
    context: str
    llm_generated_query: str
    query_executed: bool
    query_results_df_sample: pd.DataFrame
    query_results_blob_url: str
    query_remedies: str
    
    class Config:
        arbitrary_types_allowed = True


class TextToSQLExplainer:
    def __init__(self, tool_name):
        self.tool_name = tool_name
        self.results = Results(
            user_question = "",
            context = "",
            llm_generated_query = "",
            query_executed = False,
            query_results_df_sample = pd.DataFrame(),
            query_results_blob_url = "",
            query_remedies = ""
        )
        
        
    @staticmethod
    def _explain_query_with_llm_call(question, query, context):
        gpt4o_llm_config = llm_config_service.fetch_language_model(LanguageModelName.GPT_4O)
        llm = AzureChatOpenAI(
            azure_ad_token_provider=openai_token_provider,
            azure_endpoint=gpt4o_llm_config.endpoint,
            api_version=gpt4o_llm_config.api_version,
            azure_deployment=gpt4o_llm_config.deployment_name,
            model=gpt4o_llm_config.name,
            temperature=0.0,
            streaming=False,
        )
        
        context = f"""Based on the user question, explain the generated query in simple english and keep it short. 
        Mention in detail what information was used from provided context for query generation. 
        Highlight things like column names, table names, filter criteria using bold letters. If there are multiple columns, tables or filter criteria, write each in a new line.
        Here are the details: 
        User Question: {question},
        Generated Query: {query},
        Retrieved context for query generation: {context} 
        """
        
        response = llm.invoke(context)
        return response
    
    @property
    def query_explain_tool_artifact(self):
        explaination = self._explain_query_with_llm_call(
            question=self.results.user_question,
            query=self.results.llm_generated_query,
            context=self.results.context
            )
        
        return ToolArtifact(
            content=f"{explaination.content}", 
            display_name="Details", 
            tool_name=self.tool_name
        )

    @property
    def query_display_tool_artifact(self):
        return ToolArtifact(
            
            content="\n```sql\n{}\n```\n".format(self.results.llm_generated_query),
            display_name="Query", 
            tool_name=self.tool_name
        )
    
    @property        
    def query_results_display_tool_artifact(self):
        return ToolArtifact(
            content=self.results.query_results_df_sample.to_markdown(), 
            display_name="Data", 
            tool_name=self.tool_name,
            url=self.results.query_results_blob_url,
            url_display_name="Download Full Data"
        )
        
    @property
    def query_remedies_tool_artifact(self):
        gpt4o_llm_config = llm_config_service.fetch_language_model(LanguageModelName.GPT_4O)
        llm = AzureChatOpenAI(
            azure_ad_token_provider=openai_token_provider,
            azure_endpoint=gpt4o_llm_config.endpoint,
            api_version=gpt4o_llm_config.api_version,
            azure_deployment=gpt4o_llm_config.deployment_name,
            model=gpt4o_llm_config.name,
            temperature=0.0,
            streaming=False,
        )
        
        context = f"""Based on the user question, explain why it could not be answered based on the context provided and the LLM Query Generated. 
        Explain in simple english and keep it short.
        
        If the question is not related to the context, respond how I can fix the question that can yield a query that can produce insightful results.
        Do this as long as the question is somewhat related to the context. 
        If it is not related, respond how I can improve his question so it relates to the context provided.
        
        Question: {self.results.user_question},
        LLM Generated Query: {self.results.llm_generated_query},
        Retrieved context for query generation: {self.results.context}
        
        Do not mention anything about 'the context' used for query generation and do not respond with the failed the SQL QUery part of the response.
        
        Use the context only when the question is related to it but can't be answered due the the kind of question asked.
        
        Add to remedies how requesting certain fields part of the data in the context might yeild better results.
        
        Respond in 1-2 bullet points for each of these highlighted sections:
        
        Failure
        Remedies
        Sample Questions
        """
        
        remedies = llm.invoke(context)
        
        self.results.query_remedies = remedies.content
        
        return ToolArtifact(
            content=f"{remedies.content}", 
            display_name="Remedies", 
            tool_name=self.tool_name
        )
    