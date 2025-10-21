import os
from dotenv import load_dotenv

load_dotenv(override=True)

import logging
from src.clients.langfuse.manager import LangfuseManager

class LangfuseManagerRedacted(LangfuseManager):
    _instance = None

    @classmethod
    def get_instance(
        cls,
    ) -> "LangfuseManagerRedacted":
        """
        Retrieve the singleton instance of LangfuseManagerRedacted.
        If it does not already exist, create a new instance using provided parameters
        """
        if cls._instance is None:
            cls._instance = cls(
                public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
                secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
                host=os.getenv("LANGFUSE_HOST"),
                logger=logging.getLogger(__name__),
                use_redaction=True
            )
        return cls._instance
