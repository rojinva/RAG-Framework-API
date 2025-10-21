from fastapi import APIRouter, Request
from src.models import LamBotConfig, LamBotChatRequestExternal, SecurityData
from fastapi import Depends
from src.core.utils.endpoint_dependencies import  verify_api_access_external, get_security_data_external
from src.core.utils.log_trace import log_trace_event
from src.services.chat_completion.external_handler import process_chat_completion_external

chat_router_external = APIRouter(prefix="/chat_external")

@chat_router_external.post(
    "/chat_completion_external/",
    responses={503: {"detail": "503 error"}},
)
def post_chat_completion_external(
    request: Request,
    lambot_chat_request: LamBotChatRequestExternal,
    lambot_config: LamBotConfig = Depends(verify_api_access_external),
    security_data: SecurityData = Depends(get_security_data_external)
):
    """
    FastAPI endpoint to handle non-streaming external chat completion requests to LamBot.

    This route receives a chat request from an authenticated external user and delegates
    all processing to `process_chat_completion_external`, which manages the complete workflow:
    - Authenticates the user using the access token
    - Extracts the message title for conversation tracking
    - Optionally retrieves historical conversation context if a thread ID is provided
    - Calls the completion engine to generate a response
    - Validates and persists the generated messages to the MongoDB backend

    Endpoint Prefix: /chat_external/chat_completion_external/

    Args:
        trace_id:Extracts trace ID for logging and diagnostics
        request (Request): The incoming HTTP request object, used to extract headers like trace ID.
        lambot_chat_request (LamBotChatRequestExternal): The body of the request, containing:
            - `lambot_id`: The ID of the LamBot model to use
            - `messages`: User and assistant messages
            - `thread_id`: Optional thread ID to continue conversation
            - `dialog_snapshot`: Number of historical messages to retrieve for context
        lambot_config (LamBotConfig): Configuration for the LamBot model (injected via dependency).
        security_data (SecurityData): Auth information including a bearer token (injected via dependency).

    Returns:
        dict: A dictionary containing:
            - `operation_summary`: A message indicating whether a new conversation was created or an existing one updated.
            - `message`: The assistant's generated response to the chat input.

    Raises:
        HTTPException: If authentication, message validation, or database persistence fails.
    """

    trace_id = request.headers.get("x-trace-id")

    log_trace_event(
        trace_id=trace_id,
        step="user_query_received",
    )

    results=process_chat_completion_external(
        trace_id,
        request=request,
        lambot_chat_request=lambot_chat_request,
        lambot_config=lambot_config,
        security_data=security_data
        )


    return results
 

__all__ = ["chat_router_external"]
