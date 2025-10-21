from azure.identity import DefaultAzureCredential
import os
import logging
from dotenv import load_dotenv
from src.clients.constants import scopes
from src.core.cache.decorators import cache_platform
from functools import partial

load_dotenv(override=True)

logger = logging.getLogger(__name__)

os.environ["AZURE_TENANT_ID"] = os.getenv("LAMBOTS_TENANT_ID", "")
os.environ["AZURE_CLIENT_ID"] = os.getenv("LAMBOTS_CLIENT_ID", "")
os.environ["AZURE_CLIENT_SECRET"] = os.getenv("LAMBOTS_CLIENT_SECRET", "")


def make_token_provider(scope: str):
    """
    Factory function that returns a no-arg token provider (closure) for the given scope,
    cached under a dynamic key: azure_ad_token:{scope}.
    """
    @cache_platform(f"azure_ad_token:{scope}", ttl=3600)
    def _get_token() -> str:
        credential = DefaultAzureCredential()
        token_obj = credential.get_token(scopes[scope])
        return token_obj.token

    return _get_token


# Pre-scoped token providers, imported directly by clients
openai_token_provider = make_token_provider("openai")