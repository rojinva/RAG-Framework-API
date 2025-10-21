import os

from dotenv import load_dotenv
from pymongo import MongoClient
load_dotenv()


class MongoDBClient:
    _instance = None

    @classmethod
    def get_instance(cls):
        """
        Retrieve the singleton instance of MongoDBClient."""
        if cls._instance is None:
            cls._instance = MongoDBClient(
                mongodb_url=os.getenv("MONGO_DB_ENDPOINT"),
                mongodb_name=os.getenv("MONGODB_DB_NAME"),
            )
        return cls._instance
    
    def __init__(self, mongodb_url: str, mongodb_name: str) -> None:
        """
        Initializes the MongoClient by creating a single MongoClient instance
        and reusing it to query multiple collections from a given database.
        """
        # Create a single MongoClient instance and store it as an instance attribute
        self._client = MongoClient(mongodb_url)
        
        # Get the database instance once
        self.database = self._client[mongodb_name]
    
    def shutdown(self):
        """
        Shuts down the MongoDB client by closing its connection.
        """
        if self._client:
            self._client.close()
            self._client = None
