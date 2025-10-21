import os
import logging
from src.clients import MetricsApiClient
from src.models.config import LamBotConfig
from src.clients import LifespanClients
from src.core.context.vars import user_email_var
from dotenv import load_dotenv

load_dotenv(override=True)

class Helper:
    def __init__(self, lambot_config: LamBotConfig = None, name: str = None):
        if not lambot_config and not name:
            raise ValueError("Either 'lambot_config' or 'name' must be provided.")
        
        self.lambot_config = lambot_config
        self.name = name if name else self.lambot_config.name
        self.logger = self._setup_logger()
        self.metric_api_client = MetricsApiClient(
            feature_name=os.getenv("FEATURE_NAME"), user_email=user_email_var.get()
        )
       
        lifespan_clients = LifespanClients.get_instance()
        display_name = self.lambot_config.display_name if self.lambot_config else self.name
        tags = [display_name]

        if "ultron" in self.name or "cfpa" in self.name:
            self.langfuse_manager = lifespan_clients.langfuse_manager_sensitive
        elif self.name == "enterprise-lambot":
            self.langfuse_manager = lifespan_clients.langfuse_manager_redacted
        elif self.lambot_config and self.lambot_config.personal:
            self.langfuse_manager = lifespan_clients.langfuse_manager_redacted
            tags.append("personal")
        else:
            self.langfuse_manager = lifespan_clients.langfuse_manager      

        self.langfuse_manager.set_user_email(user_email_var.get())
        self.langfuse_manager.set_callback_kwargs({"tags": tags})

    def _setup_logger(self):
        logger = logging.getLogger(self.name)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        return logger

    def log_exception(self, exception):
        self.logger.error(
            f"Exception occurred in step '{self.name}': {exception}", exc_info=True
        )
