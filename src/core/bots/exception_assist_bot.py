import os
from dotenv import load_dotenv
load_dotenv(override=True)

from src.core.base import Helper
from langchain_openai import AzureChatOpenAI
from src.models import LamBotChatResponse
from src.core.tools.common.prompts import EXCEPTION_ASSIST_SYSTEM_PROMPT
from langchain_core.messages import SystemMessage, AIMessage
from src.core.database.lambot import LamBotMongoDB
from src.models.constants import LanguageModelName
from src.clients.azure import openai_token_provider

llm_config_service = LamBotMongoDB.get_instance().language_model_config_db


class ExceptionAssistBot(Helper):
    """
    A bot that converts exceptions into natural language messages for the user.
    """

    def __init__(self, lambot_display_name: str):
        """
        Initialize the ExceptionAssistBot

        Args:
            lambot_display_name (str): The name of the LamBot that encountered the exception.
        """
        self.name = "Exception Assist Bot"
        self.lambot_display_name = lambot_display_name
        super().__init__(name=self.name)

        self._system_message = self.langfuse_manager.client.get_prompt(
            name="EXCEPTION_ASSIST_SYSTEM_PROMPT",
            label=os.getenv("LANGFUSE_PROMPT_LABEL", "dev"),
            fallback=EXCEPTION_ASSIST_SYSTEM_PROMPT
        ).prompt
        self._configure_llm()
    
    def _prepare_prompt(self, exception_str: str):
        """ A method to prepare the prompt for the ExceptionAssistBot.

        Args:
            exception_str (str): An exception string to be converted into a natural language message.

        Returns:
            BaseMessages: A list of messages to be used as a prompt for the ExceptionAssistBot.
        """

        system_message_template = SystemMessage(content=self._system_message)
        exception_message_template = AIMessage(content=exception_str)

        self.langfuse_manager.callback_handler.metadata = {
            "exception_message": exception_str,
            "lambot_display_name": self.lambot_display_name
        }

        return [system_message_template, exception_message_template]

    def _configure_llm(self) -> None:
        """Private method to configure and instantiate the LLM."""
        small_model_name = os.getenv("AZURE_SMALL_MODEL_DEPLOYMENT_NAME", LanguageModelName.GPT_4O_MINI)
        small_model_spec = llm_config_service.fetch_language_model(small_model_name)

        self._llm = AzureChatOpenAI(
            azure_ad_token_provider=openai_token_provider,
            azure_endpoint=small_model_spec.endpoint,
            api_version=small_model_spec.api_version,
            azure_deployment=small_model_spec.deployment_name,
            model=small_model_spec.name,
            temperature=0.0,
            streaming=True,
            callbacks=[self.langfuse_manager.callback_handler]
        )

    async def stream_response(self, exception_str: str):
        """ A response stream from the ExceptionAssistBot.

        Args:
            exception_str (str): Exception string to be converted into a natural language message.

        Yields:
            LamBotChatResponse: A response from the ExceptionAssistBot.
        """
        prompt = self._prepare_prompt(exception_str)
        async for chunk in self._llm.astream(prompt):
            yield LamBotChatResponse(
                chunk=chunk.content, citations=[]
            ).model_dump_json() + "\n"

