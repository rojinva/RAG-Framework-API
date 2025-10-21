def filter_out_system_messages(messages):
    """
    Filters out messages with the role 'system' from the list of messages.

    Args:
        messages (list): A list of dictionaries representing the messages.
                         Each dictionary contains 'role' and 'content' keys.

    Returns:
        list: A new list of messages excluding those with the role 'system'.
    """
    return [message for message in messages if message["role"] != "system"]

def split_messages_into_history_and_last_user_query(messages):
    """
    Splits the messages into two parts:
    - Conversation History: All messages except the last user message.
    - query: The content of the last user message, which serves as the query for the assistant.

    Ensures that the last message in the messages list has the role 'user'.

    Args:
        messages (list): A list of dictionaries representing the messages.
                              Each dictionary contains 'role' and 'content' keys.

    Returns:
        tuple: A tuple containing:
            - conversation_history (list): All messages except the last user message.
            - query (str): The content of the last user message.

    Raises:
        ValueError: If the messages list is empty or the last message does not have the role 'user'.
    """
    if not messages:
        raise ValueError("The messages list cannot be empty.")

    _messages = messages.copy()

    # Filter out 'system' messages
    conversation_history = filter_out_system_messages(_messages)

    # Check if the last message has the role 'user'
    last_message_entry = conversation_history[-1]
    if last_message_entry["role"] != "user":
        raise ValueError("The last message must have the role 'user'.")

    # Extract the last user message and its content
    last_message_entry = conversation_history.pop()
    query = last_message_entry["content"]

    # Return the conversation history and the query
    return conversation_history, query
