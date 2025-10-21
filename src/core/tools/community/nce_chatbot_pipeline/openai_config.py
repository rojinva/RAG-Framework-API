import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

from langchain_openai import AzureChatOpenAI

from dotenv import load_dotenv
load_dotenv(override=True)
from src.core.database.lambot import LamBotMongoDB
from src.models.constants import LanguageModelName
from src.clients.azure import openai_token_provider


llm_config_service = LamBotMongoDB.get_instance().language_model_config_db


gpt4o_llm_config = llm_config_service.fetch_language_model(LanguageModelName.GPT_4O)

llm_4o = AzureChatOpenAI(
    azure_ad_token_provider=openai_token_provider,
    azure_endpoint=gpt4o_llm_config.endpoint,
    api_version=gpt4o_llm_config.api_version,
    azure_deployment=gpt4o_llm_config.deployment_name,
    model=gpt4o_llm_config.name,
    temperature=0.0,
    streaming=False,
)

gpt4o_mini_llm_config = llm_config_service.fetch_language_model(LanguageModelName.GPT_4O_MINI)
llm_4o_mini = AzureChatOpenAI(
    azure_ad_token_provider=openai_token_provider,
    azure_endpoint=gpt4o_mini_llm_config.endpoint,
    api_version=gpt4o_mini_llm_config.api_version,
    azure_deployment=gpt4o_mini_llm_config.deployment_name,
    model=gpt4o_mini_llm_config.name,
    temperature=0.0,
    streaming=False,
)

o3_mini_llm_config = llm_config_service.fetch_language_model(LanguageModelName.O3_MINI)
llm_o3_mini = AzureChatOpenAI(
    azure_ad_token_provider=openai_token_provider,
    azure_endpoint=o3_mini_llm_config.endpoint,
    api_version=o3_mini_llm_config.api_version,
    azure_deployment=o3_mini_llm_config.deployment_name,
    model=o3_mini_llm_config.name,
    temperature=1.0,
    streaming=False,
)

o3_mini_llm_config = llm_config_service.fetch_language_model(LanguageModelName.O3_MINI)
llm_o3_mini_low = AzureChatOpenAI(
    azure_ad_token_provider=openai_token_provider,
    azure_endpoint=o3_mini_llm_config.endpoint,
    api_version=o3_mini_llm_config.api_version,
    azure_deployment=o3_mini_llm_config.deployment_name,
    model=o3_mini_llm_config.name,
    temperature=1.0,
    streaming=False,
    reasoning_effort = "low"
)