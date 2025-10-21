import os
from dotenv import load_dotenv

load_dotenv(override=True)

from src.models.config import LanguageModelConfig
from langchain_openai import AzureChatOpenAI
from src.models.constants import LLMFeature, LanguageModelName
from src.core.database.lambot import LamBotMongoDB

llm_config_service = LamBotMongoDB.get_instance().language_model_config_db


def initialize_azure_llm_from_model_name(
    model_name: LanguageModelName,
    **kwargs
) -> AzureChatOpenAI:
    """
    Initializes an AzureChatOpenAI LLM instance based on the provided model name.

    Args:
        model_name (LanguageModelName): The name of the model to initialize.
        **kwargs: Additional keyword arguments for initializing the AzureChatOpenAI instance.

    Returns:
        AzureChatOpenAI: An initialized AzureChatOpenAI LLM instance.
    """
    llm_config = llm_config_service.fetch_language_model(model_name)
    if not llm_config:
        raise ValueError(f"Model config for {model_name} not found.")

    return initialize_azure_llm_from_spec(
        llm_config=llm_config, **kwargs
    )


def initialize_azure_llm_from_spec(
    llm_config: LanguageModelConfig,
    **kwargs
) -> AzureChatOpenAI:
    """
    Initializes an AzureChatOpenAI LLM instance based on the provided LanguageModelConfig.

    Args:
        llm_config (LanguageModelConfig): The llm spec for the Azure OpenAI models.
        **kwargs: Additional keyword arguments for initializing the AzureChatOpenAI instance.

    Returns:
        AzureChatOpenAI: An initialized AzureChatOpenAI LLM instance.

    """

    # Default seed value
    seed = os.getenv("LLM_SEED", 42)

    # Pop streaming from kwargs if it exists, otherwise default to False
    streaming = kwargs.pop('streaming', False)

    # Change key from max_completion_tokens to max_tokens if unsupported
    if LLMFeature.MAX_COMPLETION_TOKENS_PARAMETER in llm_config.unsupported_features:
        if 'max_completion_tokens' in kwargs:
            kwargs['max_tokens'] = kwargs.pop('max_completion_tokens')

    # Initialize the Azure OpenAI LLM instance
    llm_instance = AzureChatOpenAI(
        api_key=llm_config.api_key,
        azure_endpoint=llm_config.endpoint,
        api_version=llm_config.api_version,
        azure_deployment=llm_config.deployment_name,
        model=llm_config.name,
        seed=seed,
        temperature=(
            0.0 if LLMFeature.TEMPERATURE not in llm_config.unsupported_features else 1
        ),
        streaming=streaming,
        stream_options={"include_usage": True} if streaming else None,
        **kwargs
    )

    return llm_instance
