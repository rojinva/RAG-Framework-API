"""
Description:
------------
This script is designed for local development and testing of retriever tools within the ent-openai-lambots-api project.
It allows users to execute a search query against a specified retriever tool, process the results, and log a detailed summary including
score ranges, use cases, parent files, and top results.

The script is useful for debugging, validating tool outputs, and inspecting retrieved document metadata.

Environment Variable:
---------------------
TOOL_DEVELOPMENT:
    - If set to 'local', all tools will bypass obtaining prompts from Langfuse and use local prompts instead.
    - If unset or set to any other value, tools will obtain prompts from Langfuse as usual.

Instructions to Run:
--------------------
1. Ensure all dependencies are installed and your Python environment is activated.
2. Navigate to the project root directory in your terminal.
3. (Optional) To bypass Langfuse prompts, set the environment variable in the .env file before running:
        On .env
            TOOL_DEVELOPMENT=local
4. Run the script using Python:

    python src/scripts/local_tool_development.py

    - By default, it will use the tool "iplm_retriever" and the query "What is the chamber capacitance ucl for syndionGP?".
    - To use a different tool or query, modify the `tool_name` and `query` variables in the `if __name__ == "__main__":` block at the bottom of the script.
5. Check the console or log output for a summary of the search results.
"""
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
import logging
from src.models import ToolType
from src.core.tools import get_tools
from pydantic import BaseModel, Field
from langchain_core.tools import Tool
from langchain_core.callbacks import BaseCallbackHandler

logger = logging.getLogger()


def get_tool(tool_name: str) -> Tool:
    """
    Retrieve a Tool object by its name.

    Args:
        tool_name (str): The name of the tool to retrieve.

    Returns:
        Tool: The Tool object corresponding to the given name.

    Raises:
        ValueError: If the tool requires authentication.
        ValueError: If the tool is not a retriever tool.
        ValueError: If no tool with the specified name is found.
    """
    tools = get_tools()
    tool_found = None
    for tool in tools.keys():
        if tool == tool_name:
            tool_found = tools[tool]

    if not tool_found:
        msg = f"Tool not found. Select one of the following: {tools.keys()}"
        raise ValueError(msg)

    # Check for access control and tool type requirements
    if tool_found.access_control:
        raise ValueError(f"Tool '{tool_name}' requires authentication and cannot be used without proper access.")
    if tool_found.tool_type != ToolType.retriever_tool:
        raise ValueError(f"Tool '{tool_name}' is not a retriever tool. Only retriever tools are supported.")
    return tool_found

class SearchInput(BaseModel):
    search: str = Field(
        ..., 
        description="The search query string to find matching documents"
    )

class Report(BaseCallbackHandler):
    def __init__(self, query, display_chunk=False):
        self.query = query
        self.display_chunk = display_chunk
        self.search_score_key = "@search.score"
        self.index_data = None

    def process_index_response(self, documents):
        """
        Processes a list of document objects and stores their relevant data in the `index_data` attribute.
        Args:
            documents (list): A list of document objects, each expected to have `type`, `llm_context`, and `metadata` attributes.
        Side Effects:
            Updates the `index_data` attribute with a list of dictionaries, each containing the document's type, llm_context, and metadata.
        """

        self.index_data = [{"type": item.type, "llm_context": item.llm_context, **item.metadata } for item in documents]

    
    def search_score_range(self) -> tuple:
        """
        Gathers the minimum and maximum values of the search score from the index search results.

        Returns:
            tuple: A tuple containing the minimum and maximum search scores.
                   If no scores are found, returns (None, None).
        """
        scores = [item.get(self.search_score_key) for item in self.index_data if self.search_score_key in item]
        if not scores:
            return None, None
        return min(scores), max(scores)
    
    def top_five_scores(self):
        """
        Returns the top five items from the index search results sorted by the key @search.score.
        The method sorts the list of dictionaries `self.index_data` in descending order based on the value of `self.search_score_key` in each dictionary. 
        If the key is missing, a default value of 0 is used. It then returns the first five items from the sorted list.
        Returns:
            list: A list containing up to five dictionaries with the highest scores.
        """
        sorted_data = sorted(self.index_data, key=lambda x: x.get(self.search_score_key, 0), reverse=True)
        return sorted_data[:5]
    
    def _collect_unique_field(self, field_name):
        return list({item.get(field_name) for item in self.index_data if item.get(field_name)})

    def all_use_cases(self):
        return self._collect_unique_field("use_case")

    def all_parent_files(self):
        return self._collect_unique_field("parent_filename")

    def on_retriever_end(self, documents, run_id, parent_run_id, tags):
        """
        Handles the end of a retrieval process by processing the retrieved documents and logging a summary of the search results.

        Args:
            documents (list): The list of retrieved documents to process.
            run_id: The unique identifier for this run.
            parent_run_id: The unique identifier for the parent run.
            tags: Any tags associated with this run.

        Side Effects:
            - Processes the index response using the provided documents.
            - Logs a formatted summary of the search query, score range, use cases, parent files, and details of the top 5 results.
            - Optionally logs the content chunk of each result if `self.display_chunk` is True.

        Logging Details:
            - Query string used for retrieval.
            - Score range of the search results.
            - Associated use cases and parent files.
            - Detailed information for the top 5 results, including metadata fields and optionally the content chunk.
        """

        self.process_index_response(documents)
        logger.info("=" * 60)
        logger.info("🔍 Search Results Summary")
        logger.info("=" * 60)
        min_score, max_score = self.search_score_range()
        logger.info(f"Query            : {self.query}")
        logger.info(f"Score Range      : {min_score} - {max_score}")
        logger.info(f"Use Cases        : {', '.join(self.all_use_cases()) or 'None'}")
        logger.info(f"Parent Files     : {', '.join(self.all_parent_files()) or 'None'}")
        logger.info("-" * 60)
        logger.info("Top 5 Results:")
        for i, item in enumerate(self.top_five_scores(), 1):
            logger.info("-" * 20)
            logger.info(f"Result #{i}:")
            keys = ['@search.score', 'parent_filename', 'parent_url', 'parent_path', 'use_case', 'storage_modified', 'source_modified','source_created']
            for key in keys:
                logger.info(f"  {key}: {item[key]}")
            if self.display_chunk:
                logger.info(f"  chunk: {item['chunk']}")
        logger.info("=" * 60)


def main(tool_name, query, display_chunk):
    """
    Executes a search using the specified tool and query, then logs the results.

    Args:
        tool_name (str): The name of the tool to use for the search.
        query (str): The search query string.
        display_chunk (int): The number of results or chunk size to display in the report.

    Returns:
        None
    """
    tool = get_tool(tool_name)
    tool.set_display_names([tool_name])
    tool.invoke(query, {"callbacks":[Report(tool_name, display_chunk)]})

if __name__ == "__main__":
    tool_name = "iplm_retriever"
    query = "What is the chamber capacitance ucl for syndionGP?"
    display_chunk = False
    main(tool_name, query, display_chunk)