from fastapi import APIRouter, Depends, HTTPException, Path
from src.models import  SecurityData
from src.core.utils.auth_helpers import get_user_info
from src.core.utils.endpoint_dependencies import  get_security_data_external
from src.core.common.constants import AuthScheme
from src.core.database import LamBotMongoDB

db_router_external = APIRouter(prefix="/entity")

LAMBOTCONVERSATION_EXTERNAL_NOT_FOUND = "LamBotConversation External not found"

@db_router_external.get(
    "/thread/{thread_id}",
    responses={503: {"detail": "503 error"}}
)
def fetch_conversation_external(
    thread_id: str = Path(..., description="The thread message ID"),
    security_data: SecurityData = Depends(get_security_data_external)
):
    """
    Fetch a single conversation by `thread_id` for the authenticated user.

    Args:
        thread_id (str): The ID of the conversation thread to retrieve.
        request (Request): FastAPI request object (optional).
        security_data (SecurityData): Contains the bearer token for authentication.

    Returns:
        dict: A conversation document including messages and metadata.
    """
    try:
       username = get_user_info(security_data.bearer_token.credentials.split(AuthScheme.BEARER)[-1]).get("email")
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    query = {
        "username":username,
    }
    if thread_id.strip():
        query["threadId"] = thread_id
    # Instantiate the service directly here
    try:
        response = LamBotMongoDB.get_instance().conversations_external_db.fetch_conversation(query)
        if "not found" in response.get("message", ""):
            raise HTTPException(status_code=404, detail=LAMBOTCONVERSATION_EXTERNAL_NOT_FOUND)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return response

 
@db_router_external.get(
    "/threads/",
    responses={503: {"detail": "503 error"}}
)
def fetch_conversation_externals(
    security_data: SecurityData = Depends(get_security_data_external)
):
    """
    Fetch all conversation threads for the authenticated user.

    Args:
        request (Request): FastAPI request object (optional).
        security_data (SecurityData): Contains the bearer token for authentication.

    Returns:
        List[dict]: A list of conversation documents.
    """

    try:
        username = get_user_info(security_data.bearer_token.credentials.split(AuthScheme.BEARER)[-1]).get("email")
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    query = {
        "username":username,
    }
    # Instantiate the service directly here
    try:
        response = LamBotMongoDB.get_instance().conversations_external_db.fetch_conversation(query)
        if "not found" in response.get("message", ""):
            raise HTTPException(status_code=404, detail=LAMBOTCONVERSATION_EXTERNAL_NOT_FOUND)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return response

 
@db_router_external.delete(
    "/thread/{thread_id}",
    responses={503: {"detail": "503 error"}}
)
def delete_conversation_external(
    thread_id: str = Path(..., description="The thread message ID"),
    security_data: SecurityData = Depends(get_security_data_external)
):
    """
    Delete a specific conversation thread by `thread_id` for the authenticated user.

    Args:
        thread_id (str): The ID of the conversation thread to delete.
        request (Request): FastAPI request object (optional).
        security_data (SecurityData): Contains the bearer token for authentication.

    Returns:
        dict: Status message and count of deleted records.
    """
    try:
        username = get_user_info(security_data.bearer_token.credentials.split(AuthScheme.BEARER)[-1]).get("email")
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    query = {
        "username":username,
    }
    if thread_id.strip():
        query["threadId"] = thread_id

    # Instantiate the service directly here
    try:
        response = LamBotMongoDB.get_instance().conversations_external_db.fetch_conversation(query)
        if "No matching" in response.get("message", ""):
            raise HTTPException(status_code=404, detail=LAMBOTCONVERSATION_EXTERNAL_NOT_FOUND)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return response


 
@db_router_external.delete(
    "/threads/",
    responses={503: {"detail": "503 error"}}
)
def delete_conversation_externals(
    security_data: SecurityData = Depends(get_security_data_external)
):
    """
    Delete all conversations associated with the authenticated user.

    Args:
        request (Request): FastAPI request object (optional).
        security_data (SecurityData): Contains the bearer token for authentication.

    Returns:
        dict: Status message and count of deleted records.
    """
    try:
        username = get_user_info(security_data.bearer_token.credentials.split(AuthScheme.BEARER)[-1]).get("email")
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    query = {
        "username":username,
    }

    # Instantiate the service directly here
    try:
        response = LamBotMongoDB.get_instance().conversations_external_db.delete_conversation(query)
        if "Not matching" in response.get("message", ""):
            raise HTTPException(status_code=404, detail=LAMBOTCONVERSATION_EXTERNAL_NOT_FOUND)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return response


__all__ = ["db_router_external"]
