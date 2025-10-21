from fastapi import HTTPException
from src.models import LamBotChatRequest, LamBotConfig
from src.core.bots import LamBot, ExceptionAssistBot
from src.core.utils.log_trace import log_trace_event
from src.core.chat import ConversationEngine
from dotenv import load_dotenv
import warnings

load_dotenv(override=True)

async def chat_completion(
    lambot_chat_request: LamBotChatRequest, lambot_config: LamBotConfig, trace_id: str,
):
    bot = None  # Initialize bot to None to prevent UnboundLocalError
    try:
        bot_config = lambot_config
        query_config = lambot_chat_request.query_config
        messages = lambot_chat_request.messages
        file_attachments = lambot_chat_request.file_attachments or []

        # Add logging for file attachments (e.g. file count, types, names)


        # Assembly
        # Configures the bot with the provided query config if it's not None, otherwise uses the default query config
        bot = LamBot(bot_config=bot_config, query_config=query_config, file_attachments=file_attachments)

        # Action
        # Instantiate the conversation handler with the bot
        conversation_engine = ConversationEngine(bot)

        log_trace_event(
            trace_id=trace_id,
            step="conversation_engine_started",
        )

        async for response in conversation_engine.generate_response(messages=messages, trace_id=trace_id, streaming=True):
            yield response

    except Exception as e:
        # If the error is a ValueError, raise a 422 Unprocessable Entity error
        if isinstance(e, ValueError):
            raise HTTPException(422, f"422 error: {e}")
        
        exception_str = str(e)
        warnings.warn(f"Streaming error: {exception_str}") # This is a warning, not an error (for logging purposes)
        lambot_display_name = bot_config.display_name

        exception_assist_bot = ExceptionAssistBot(lambot_display_name)
        
        # Only try to log to metric API if bot was successfully initialized
        if bot and hasattr(bot, 'metric_api_client'):
            bot.metric_api_client.make_async_log_exceptions_request(
                exception_message=f"Exception in chat completion for lamBot {bot_config.id} with exception "
                                  f"{exception_str} with correlationID: {bot.metric_api_client.correlation_id}",    
            )
        
        async for response in exception_assist_bot.stream_response(exception_str):
            yield response
