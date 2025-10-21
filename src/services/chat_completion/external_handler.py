from typing import List, Dict, Any, Union, Optional
import os
from src.clients import LifespanClients
from src.core.database import LamBotMongoDB
from fastapi import HTTPException
from src.core.utils.auth_helpers import get_user_info
from src.services.chat_completion.external import (
    chat_completion_non_streaming,
    fetch_history_context,
    handle_chat_completion
)
from src.core.common.constants import AuthScheme

import asyncio


def validate_and_update_conversation(
    lambot_id: str,
    thread_id: Optional[str],
    new_messages: List[Dict],
    title: str,
    username: str
) -> str:
    """
    Orchestrates the creation or update of a LamBot conversation document in MongoDB.
    Uses ThreadService for actual operations.
    """

    if not LamBotMongoDB.get_instance().conversations_external_db.user_exists(username):
        return LamBotMongoDB.get_instance().conversations_external_db.create_new_user_conversation(
            lambot_id, thread_id, new_messages, title, username
        )

    if not thread_id:
        return LamBotMongoDB.get_instance().conversations_external_db.start_new_thread_for_user(
            lambot_id, username, new_messages, title
        )

    return LamBotMongoDB.get_instance().conversations_external_db.update_existing_thread(
        lambot_id, thread_id, username, new_messages
    )

 
 
def get_message_title(message_content: str) -> str:
    """
    Extracts the title of the message using Azure OpenAI.

    This function uses the LangChain Azure OpenAI client to process the content of the message
    and extract a title based on the provided content.

    Args:
        message_content (str): The content of the message.

    Returns:
        str: The extracted title of the message.

    Raises:
        ValueError: If the message content is missing or the OpenAI API fails.
    """
    if not message_content:
        raise ValueError("Message content is missing.")

    # Configure Azure OpenAI client
    azure_client = LifespanClients.get_instance().azure_openai
    # Generate a title for the message
    try:
        # Create messages as LangChain message objects
        response = azure_client.azure_use_region_client.chat.completions.create(
                            model=os.getenv("AZURE_SMALL_MODEL_DEPLOYMENT_NAME"),
                            messages=[
                                {"role": "system", "content": "You are an AI assistant that generates concise titles for messages."},
                                {"role": "user", "content": f"Generate a concise and descriptive title for the following message:\n\n{message_content}"}
                            ],
                            temperature=0.3
        )
        title = response.choices[0].message.content

        if not title:
            raise ValueError("Failed to generate a title.")
        return title
    except Exception as e:
        raise ValueError(f"Error generating title: {str(e)}")


def process_chat_completion_external(
    trace_id: str,
    request,
    lambot_chat_request,
    lambot_config,
    security_data
    ) -> Dict[str, Union[str, Any]]:
    """
    Full pipeline handler for LamBot external chat completion requests.
    This function performs the end-to-end logic for non-streaming chat completion via LamBot.
    It is invoked by the `/chat_completion_external/` FastAPI route and performs the following steps:
    Steps:
        1. Extracts trace ID for logging and diagnostics.
        2. Retrieves and authenticates the user ID using the provided bearer token.
        3. Extracts the title from the latest user message to use as conversation metadata.
        4. Optionally fetches historical conversation context based on thread ID and snapshot count.
        5. Calls the non-streaming completion service to generate a model response.
        6. Processes the raw response into a structured message format.
        7. Validates the generated message using the `MessageConfig` Pydantic schema.
        8. Updates or inserts the conversation thread into the MongoDB collection.
    Args:
        trace_id (str): Unique trace identifier for tracking the request.
        request (Request): FastAPI request object used to extract headers (e.g., trace ID).
        lambot_chat_request (LamBotChatRequestExternal): The user input request with conversation context.
        lambot_config (LamBotConfig): Model configuration and runtime parameters.
        security_data (SecurityData): Security context containing bearer token and metadata.
    Returns:
        Dict[str, Union[str, Any]]: A dictionary with:
            - "operation_summary": A log-style message describing insert/update.
            - "message": The full assistant model output.
    Raises:
        HTTPException: If user authentication or MongoDB persistence fails.
    """
    lambotid: str = lambot_chat_request.lambot_id
    thread_id: str = lambot_chat_request.thread_id
    history_context_messages: List[Dict[str, str]] = []
    # Step 1: Retrieve User name
    username = get_user_info(security_data.bearer_token.credentials.split(AuthScheme.BEARER)[-1]).get("email")
    # Step 2: Generate title from latest user message
    try:
        user_messages = [msg for msg in lambot_chat_request.messages if msg.get('role') == 'user']
        if not user_messages:
            raise ValueError("No user message found in the request.")
        message_content: str = user_messages[-1]['content']
        title: str = get_message_title(message_content)
    except (ValueError, IndexError, KeyError) as e:
        return {"error": f"Message title extraction failed: {str(e)}"}
    # Step 3: Fetch context history
    if thread_id and str(thread_id).strip():
        history_context_messages = fetch_history_context(lambotid, thread_id, username)
    # Step 4: Generate chat completion
    if asyncio.iscoroutinefunction(chat_completion_non_streaming):
        completion = asyncio.run(chat_completion_non_streaming(
            lambot_chat_request,
            lambot_config,
            trace_id,
            history_context_messages
        ))
    # Step 5: Process into message schema
    new_messages = handle_chat_completion(message_content, completion)
    # Step 6: Save to MongoDB
    try:
        operation_summary = validate_and_update_conversation(
            lambotid,
            thread_id,
            new_messages,
            title,
            username
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Failed to push conversation: {str(e)}")
    return {
        "operation_summary": operation_summary,
        "message": completion
    }
 
 