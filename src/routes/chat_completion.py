from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from src.models import LamBotChatRequest, LamBotConfig, LamBotChatResponse
from src.services.chat_completion.internal import chat_completion
from fastapi import Depends
from src.core.utils.endpoint_dependencies import verify_api_access
from src.core.utils.log_trace import log_trace_event

chat_router = APIRouter(prefix="/chat")


@chat_router.post(
    "/chat_completion/",
    response_model=LamBotChatResponse,
    responses={503: {"detail": "503 error"}},
)
def get_chat_completion(
    request: Request,
    lambot_chat_request: LamBotChatRequest,
    lambot_config: LamBotConfig = Depends(verify_api_access),
):
    """
    Get chat completion.
    """
    trace_id = request.headers.get("x-trace-id")

    log_trace_event(
        trace_id=trace_id,
        step="user_query_received",
    )
    
    completion = StreamingResponse(
        chat_completion(lambot_chat_request, lambot_config, trace_id),
        media_type="text/event-stream",
    )
    return completion


__all__ = ["chat_router"]
