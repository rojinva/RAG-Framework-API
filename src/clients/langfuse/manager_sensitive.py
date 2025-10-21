import os
from dotenv import load_dotenv

load_dotenv(override=True)

import logging
from src.clients.langfuse.manager import LangfuseManager

class LangfuseManagerSensitive(LangfuseManager):
    _instance = None

    @classmethod
    def get_instance(
        cls,
    ) -> "LangfuseManagerSensitive":
        """
        Retrieve the singleton instance of LangfuseManagerSensitive.
        If it does not already exist, create a new instance using provided parameters
        """
        if cls._instance is None:
            cls._instance = cls(
                public_key=os.getenv("LANGFUSE_PUBLIC_KEY_SENSITIVE", None),
                secret_key=os.getenv("LANGFUSE_SECRET_KEY_SENSITIVE", None),
                host=os.getenv("LANGFUSE_HOST"),
                logger=logging.getLogger(__name__)
            )
        return cls._instance
