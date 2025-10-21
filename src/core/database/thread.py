from typing import List, Dict, Any, Optional
import uuid
from pymongo.collection import Collection
from dotenv import load_dotenv
from src.models.functions import datetime_now
from src.models.config import ConversationDocumentConfig, MessageConfig

load_dotenv()


class ThreadDB:
    """
    Service class for managing user conversations stored in the `ThreadDB` MongoDB collection.
    Provides functionality to fetch message history, retrieve full conversation threads, and delete records.
    """

    def __init__(self, collection: Collection):
        """
        Initialize the ThreadDB with a MongoDBService instance.

        Args:
            collection (MongoDBService): A service instance for MongoDB operations on the 'ThreadDB' collection.
        """
        self.collection = collection

    def fetch_conversation(self, query: dict) -> Dict[str, Any]:
        """
        Fetch the full conversation thread matching the query.

        Args:
            query (dict): Query filter that may include 'user_name', and 'thread_id'.

        Returns:
            Dict[str, Any]: Contains:
                - 'lambot_id': The requested lambot ID.
                - 'history': A list of thread objects with 'thread_id' and associated 'messages',
                             or None if no matching conversation was found.

        Raises:
            RuntimeError: If the database fetch operation fails.
        """
        try:
            docs = list(self.collection.find(query))

            filtered = [
                {
                    "threadId": doc.get("threadId"),
                    "messages": doc.get("messages")
                }
                for doc in docs
            ]

            if not filtered:
                return {
                    "message": f"Conversation not found for thread_id: {query.get('threadId')}",
                    "history": None
                }

            return {
                "message": filtered
            }

        except Exception as e:
            raise RuntimeError(f"Failed to fetch conversation: {str(e)}")

    def fetch_n_messages(self, query: dict) -> List:
        """
        Fetches the latest N messages from the conversation based on the query.

        Args:
            query (dict): MongoDB query to match the conversation(s), e.g., userId, model, thread_id.
         
        Returns:
            List[Dict[str, str]]: A list of messages with role ('user' or 'system') and content.
        """
        try:
            docs = self.collection.find(query)
            user_messages = []

            for doc in docs:
                if "messages" in doc:
                    sorted_messages = sorted(
                        doc["messages"],
                        key=lambda x: x.get("assistant", {}).get("createdAt", ""),
                        reverse=True
                    )
                    for message in sorted_messages:
                        if "assistant" in message and message["assistant"] and "chunk" in message["assistant"]:
                            user_messages.append({"role": "system", "content": message["assistant"]["chunk"]})
                        if "user" in message and message["user"] and "content" in message["user"]:
                            user_messages.append({"role": "user", "content": message["user"]["content"]})

            return user_messages

        except Exception as e:
            raise RuntimeError(f"Failed to fetch conversation messages: {str(e)}")

    
    def delete_conversation(self, query: dict) -> Dict[str, Any]:
        """
        Deletes one or more conversations based on the query:
        - If 'thread_id' is present: deletes specific thread
        - If only 'user_id' is present: deletes all threads for the user

        Args:
            query (dict): MongoDB query to filter conversations (must include user_id, may include thread_id)

        Returns:
            dict: {
                "message": Description of the operation result,
                "deleted_count": Number of documents deleted
            }

        Raises:
            RuntimeError: If deletion fails
        """
        try:
            # Extract values for clear logging / messages
            thread_id = query.get("threadId")
            # Perform deletion
            result = self.collection.delete_many(query)

            if result.deleted_count > 0:
                msg_prefix = "Conversation(s) deleted successfully "
            else:
                msg_prefix = "No matching conversation(s) found for deletion with"

            # Compose message parts
            msg_parts = []

            if thread_id:
                msg_parts.append(f"thread_id: {thread_id}")

            message = f"{msg_prefix} " + ", ".join(msg_parts) if msg_parts else f"{msg_prefix} given query"

            return {
                "message": message,
                "deleted_count": result.deleted_count
            }

        except Exception as e:
            raise RuntimeError(f"Failed to delete conversation: {str(e)}")
    
    def user_exists(self, username: str) -> bool:
            
        """
        Check if a user with the given username exists in the collection.

        Args:
        username (str): The username to search for in the collection.

        Returns:
        bool: True if a user with the specified username exists, False otherwise.
        """

        return self.collection.find_one({"username": username}) is not None

    def create_new_user_conversation(self, lambot_id: str, thread_id: Optional[str],
                                     new_messages: List[Dict], title: str, username: str) -> str:
        
        """
        Creates a new conversation document for a new user.

        Args:
            collection: The MongoDB collection instance.
            lambot_id (str): Identifier of the LamBot/chatbot model.
            thread_id (Optional[str]): Root thread_id, or None to auto-generate.
            user_obj_id (ObjectId): MongoDB ObjectId of the user.
            new_messages (List[Dict]): Messages to be stored in the new document.
            title (str): Title of the conversation.

        Returns:
            str: Status message confirming creation of the new document.
        """
        final_root_id = thread_id if thread_id else str(uuid.uuid4())
        validated_messages = [MessageConfig(**msg) for msg in new_messages]

        doc = ConversationDocumentConfig(
            title=title,
            thread_id=final_root_id,
            messages=validated_messages,
            lambot_id=lambot_id,
            created_at=datetime_now(),
            username=username
        )
        self.collection.insert_one(doc.model_dump(by_alias=True, exclude_none=True,mode="json"))
        return f"[New User] Created new document with thread_id: {final_root_id}"

    def start_new_thread_for_user(self, lambot_id: str, username: str,
                                  new_messages: List[Dict], title: str) -> str:
        """
        Starts a new conversation thread for an existing user and LamBot model.

        Args:
            collection: The MongoDB collection instance.
            lambot_id (str): Identifier of the LamBot/chatbot model.
            username (ObjectId): MongoDB ObjectId of the user.
            new_messages (List[Dict]): Messages for the new thread.
            title (str): Title of the conversation.

        Returns:
            str: Status message confirming creation of the new thread.

        Raises:
            ValueError: If the user does not exist for the specified LamBot model.
        """
        if not self.collection.find_one({"username": username}):
            raise ValueError("[Error] Invalid Username: No matching record found in the database.")
      

        validated_messages = [MessageConfig(**msg) for msg in new_messages]
        generated_id = str(uuid.uuid4())

        doc = ConversationDocumentConfig(
            title=title,
            thread_id=generated_id,
            messages=validated_messages,
            lambot_id=lambot_id,
            created_at=datetime_now(),
            username=username
        )
        self.collection.insert_one(doc.model_dump(by_alias=True, exclude_none=True,mode="json"))
        return f"[New Thread] Started new conversation with thread_id: {generated_id}."

    def update_existing_thread(self, lambot_id: str, thread_id: str, username: str,
                               new_messages: List[Dict]) -> str:
        """
        Appends messages to an existing conversation thread.

        Args:
            collection: The MongoDB collection instance.
            lambot_id (str): Identifier of the LamBot/chatbot model.
            thread_id (str): thread_id message of the thread to update.
            username (ObjectId): MongoDB ObjectId of the user.
            new_messages (List[Dict]): Messages to append to the thread.

        Returns:
            str: Status message confirming successful update.

        Raises:
            ValueError: If the document is not found or messages field is invalid.
        """
        existing_doc = self.collection.find_one({
            "threadId": thread_id,
            "username": username
        })

        if not existing_doc:
            raise ValueError(f"[Error] Invalid thread_id: '{thread_id}'")

        if not isinstance(existing_doc.get("messages", []), list):
            raise ValueError("[Error] The 'messages' field is not a list. Skipping update.")

        try:
            validated_messages = [MessageConfig(**m) for m in new_messages]
        except ValueError:
            raise ValueError("[Validation Error] Assistant message validation failed")

        self.collection.update_one(
            {
                "lambotId": lambot_id,
                "threadId": thread_id,
                "username": username
            },
            {
                "$push": {
                    "messages": {
                        "$each": [msg.model_dump(by_alias=True, exclude_none=True,mode="json") for msg in validated_messages]
                    }
                }
            }
        )
        return f"[Updated] Appended to thread_id: {thread_id}"
