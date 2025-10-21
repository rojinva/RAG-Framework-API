import pyodbc
import os
import logging
from dotenv import load_dotenv

load_dotenv(override=True)

logger = logging.getLogger(__name__)

class SynapseClient:
    _instance = None

    @classmethod
    def get_instance(cls):
        """
        Retrieve the singleton instance of SynapseClient.
        """
        if cls._instance is None:
            cls._instance = SynapseClient()
        return cls._instance

    def __init__(self):
        """
        Initialize the SynapseClient with a connection and cursor.
        """
        if hasattr(self, '_initialized') and self._initialized:
            logger.info("SynapseClient is already initialized.")
            return

        server = os.getenv("OPENAI_SYNAPSE_SERVER")
        database = os.getenv("OPENAI_SYNAPSE_DATABASE")
        username = os.getenv("OPENAI_SYNAPSE_USERNAME")
        password = os.getenv("OPENAI_SYNAPSE_SECRET")
        authentication = 'ActiveDirectoryPassword'
        driver = '{ODBC Driver 17 for SQL Server}'
        
        if not all([server, database, username, password]):
            error_msg = "Synapse environment variables must be provided."
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        params = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};AUTHENTICATION={authentication}"
        try:
            self.connection = pyodbc.connect(params)
            self.cursor = self.connection.cursor()
            logger.info("SynapseClient initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize SynapseClient: {e}")
            raise

        self._initialized = True

    def execute_query(self, query):
        """
        Execute a SQL query and return the results.

        Args:
            query (str): The SQL query to execute.

        Returns:
            List[tuple]: The results of the query.
        """
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return []

    def shutdown(self):
        """
        Close the cursor and connection.
        """
        if self.cursor:
            self.cursor.close()
            logger.info("Synapse cursor closed.")
        if self.connection:
            self.connection.close()
            logger.info("Synapse connection closed.")
