import logging
import os
from typing import Optional
from langfuse.client import Langfuse
from langfuse.callback import CallbackHandler as LangFuseCallbackHandler
from langchain.callbacks import StdOutCallbackHandler
from src.clients.langfuse.utils import TraceSanitizer

from dotenv import load_dotenv

load_dotenv(override=True)


class LangfuseManager:
    _instance = None

    def __init__(
        self,
        public_key: str,
        secret_key: str,
        host: str,
        logger: logging.Logger,
        use_redaction: bool = False,
        user_email: Optional[str] = None,
        callback_kwargs: Optional[dict] = None,
    ):
        # If already initialized, do not reinitialize
        if hasattr(self, '_initialized') and self._initialized:
            logger.info("LangfuseManager is already initialized.")
            return

        self.logger = logger
        self.public_key = public_key
        self.secret_key = secret_key
        self.host = host
        self.user_email = user_email
        self.callback_kwargs = callback_kwargs
        self.is_initialized = False

        # Initialize the Langfuse client
        self.client = Langfuse(
            public_key=self.public_key,
            secret_key=self.secret_key,
            host=self.host,
        )

        if self.client:
            self.is_initialized = True

        trace_sanitizer = TraceSanitizer()

        # Create the LangFuse callback handler
        self._callback = LangFuseCallbackHandler(
            public_key=self.public_key,
            secret_key=self.secret_key,
            host=self.host,
            mask=trace_sanitizer.mask if use_redaction else None,
        )
        self._initialized = True



    def get_prompt(self, prompt_name: str, fallback_prompt: str, label: str = None) -> str:
        """
        Get prompt from Langfuse with fallback support. 
        Returns fallback prompt directly when environment is Local.
        """
        tool_environment = os.getenv("TOOL_ENVIRONMENT", "").lower()
        
        if tool_environment == "local":
            self.logger.info(f"Local environment detected, using fallback prompt for: {prompt_name}")
            return fallback_prompt
        
        try:
            if label is None:
                label = os.getenv("LANGFUSE_PROMPT_LABEL", "dev")
            
            prompt_response = self.client.get_prompt(
                name=prompt_name, 
                label=label, 
                fallback=fallback_prompt
            )
            return prompt_response.prompt
        except Exception as e:
            self.logger.warning(f"Failed to get prompt {prompt_name} from Langfuse, using fallback: {e}")
            return fallback_prompt

    @classmethod
    def get_instance(
        cls,
    ) -> "LangfuseManager":
        """
        Retrieve the singleton instance of LangfuseManager.
        If it does not already exist, create a new instance using provided parameters or default environment values.
        """
        if cls._instance is None:
            cls._instance = LangfuseManager(
                public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
                secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
                host=os.getenv("LANGFUSE_HOST"),
                logger=logging.getLogger(__name__),
                use_redaction=False
            )
        return cls._instance

    @property
    def callback_handler(self):
        if self.is_initialized:
            return self._callback
        else:
            return StdOutCallbackHandler()

    def set_user_email(self, user_email: str):
        self.user_email = user_email
        if hasattr(self, '_callback'):
            self._callback.user_id = self.user_email

    def set_callback_kwargs(self, callback_kwargs: dict):
        self.callback_kwargs = callback_kwargs
        use_masker = "tags" in self.callback_kwargs and "Enterprise LamBot" in self.callback_kwargs.get("tags", [])
        trace_sanitizer = TraceSanitizer()

        if hasattr(self, '_callback'):
            self._callback.mask = trace_sanitizer.mask if use_masker else None
            self._callback.tags = self.callback_kwargs.get("tags", [])