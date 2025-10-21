import traceback
from langchain_core.prompts import PromptTemplate
from typing import Union, List, Dict, Type
from langchain.chains.sql_database.query import create_sql_query_chain
import pandas as pd
from src.core.tools.community.nce_chatbot_pipeline.summarizer import Summarizer
import re
import json
import time
import traceback
from src.core.base import LamBotTool
from src.models.tool import ToolArtifact
from src.models.constants import ToolType
from src.models.base import ConfiguredBaseModel
from pydantic import BaseModel, Field, PrivateAttr
import os
from src.core.tools.community.nce_chatbot_pipeline.openai_config import llm_4o, llm_o3_mini, llm_o3_mini_low
from src.core.tools.community.nce_chatbot_pipeline.langchain_classes import SQLDatabase, LazyReflectMetadata
from typing import Optional, Tuple
import logging
from concurrent.futures import ThreadPoolExecutor
from .prompts import prompts

from src.clients import LifespanClients

# ----------------------------------------------------------------------------
# Tool Specification Model
# ----------------------------------------------------------------------------
class ETSToolSpec(ConfiguredBaseModel):
    """
    Specification for the ETS tool.

    Attributes:
        tool_name (str): Name of the tool.
        tool_description (str): Description of the tool.
        top_k (int): Number of records to return unless instructed otherwise.
        prompts (Dict[str, Tuple[str, str]]): Prompts for the tool, where each key maps to a tuple 
            (prompt_name, fallback_prompt).
    """
    tool_name: str = Field(..., description="Name of the tool.")
    tool_description: str = Field(..., description="Description of the tool.")
    top_k: int = Field(..., description="Number of records to return.")
    prompts: Dict[str, Tuple[str, str]] = Field(..., description="Prompts for the tool.")


# ----------------------------------------------------------------------------
# Input Model
# ----------------------------------------------------------------------------
class ToolInput(BaseModel):
    """
    Input to the tool.
    
    Attributes:
        query (str): User question to be processed by the tool.
    """
    query: str = Field(description="User question to be processed by the tool.")


# ----------------------------------------------------------------------------
# Helper to Generate Prompt Property
# ----------------------------------------------------------------------------
def make_prompt_property(key: str):
    """
    Returns a property that retrieves the dynamic prompt from Langfuse.
    It looks up the key first in self.tool_spec.prompts, falling back to the module-level prompts dict.
    """
    def prop(self) -> str:
        # Look up key in tool_spec.prompts, otherwise from the fallback prompts dict
        entry = self.tool_spec.prompts.get(key, None)
        if entry is None:
            entry = prompts.get(key)
        if entry is None:
            raise ValueError(f"No prompt entry found for key: {key}")
        prompt_name, fallback = entry

        client = LifespanClients.get_instance().langfuse_manager
        prompt = client.get_prompt(
            prompt_name=prompt_name,
            fallback_prompt= fallback
        )

        return prompt
    return property(prop)


# ----------------------------------------------------------------------------
# Class Decorator to Add Prompt Properties Automatically
# ----------------------------------------------------------------------------
def add_prompt_properties(cls: Type) -> Type:
    """
    Iterates over keys in the fallback prompts dictionary and adds an @property to the class for each key.
    The property name is the lower-case version of the key.
    """
    for key in prompts.keys():
        prop_name = key.lower()  # e.g. "PIPELINE_CREATOR_PROMPT" becomes "pipeline_creator_prompt"
        # Only attach property if not already defined
        if not hasattr(cls, prop_name):
            setattr(cls, prop_name, make_prompt_property(key))
    return cls


# ----------------------------------------------------------------------------
# ETSChatBotTool with Dynamically Generated Prompt Properties
# ----------------------------------------------------------------------------
@add_prompt_properties
class ETSChatBotTool(LamBotTool):
    """
    ETSChatBotTool contains all functions for the ETS chatbot project.
    All prompt strings (fields, examples, pipeline steps, etc.) are retrieved on demand
    via dynamically generated properties.
    
    Attributes:
        args_schema (Type[BaseModel]): Schema for the tools input arguments.
        db (Optional[SQLDatabase]): The database connection object.
    """
    args_schema: Type[BaseModel] = ToolInput
    db: Optional[SQLDatabase] = None

    # Use a private attribute for tool_spec so that pydantic does not enforce it as a model field.
    _tool_spec: ETSToolSpec = PrivateAttr()

    @property
    def tool_spec(self):
        """
        Public property to access the tool specification.
        """
        return self._tool_spec

    def __init__(self, name: str, description: str, tool_spec: ETSToolSpec, tool_type: ToolType):
        #pass tool_spec to the super-class if needed, or omit it.
        super().__init__(name=name, description=description, tool_type=tool_type)
        self._tool_spec = tool_spec
        self.description = self.pipeline_tool_description

    @classmethod
    def from_tool_spec(cls, tool_spec: ETSToolSpec):
        name = tool_spec.tool_name
        description = tool_spec.tool_description
        tool_type = ToolType.non_retriever_tool
        return cls(name=name, description=description, tool_spec=tool_spec, tool_type=tool_type)

    
    # ----------------------------------------------------------------------------
    # Core helper methods
    # ----------------------------------------------------------------------------

    def _append_to_message_log(self, message_log: str, additional_message: str) -> str:
        """
        Append a new message to the message log.

        Args:
            message_log (str): Original message log.
            additional_message (str): Message to append.

        Returns:
            str: Updated message log.
        """
        return message_log + additional_message

    def _strip_markdown_notation(self, content: Union[str, dict]) -> str:
        """
        Strip markdown notation from the input content.

        Args:
            content (Union[str, dict]): Input string or dictionary containing markdown notation.

        Returns:
            str: String with markdown notation removed.
        """
        if isinstance(content, dict):
            content = str(content["question_json"].content)

        # Remove SQL markdown notation
        sql_pattern = re.compile(r"```sql\n(.*?)\n```", re.DOTALL | re.IGNORECASE) 
        content = sql_pattern.sub(r"\1", content)

        # Remove JSON markdown notation
        json_pattern = re.compile(r"```json\n(.*?)\n```", re.DOTALL)
        content = json_pattern.sub(r"\1", content)

        return content
    
    def _is_response_empty(self, invoked_response) -> bool:
        """
        Check if the invoked response is empty.

        Args:
            invoked_response: Response to check.

        Returns:
            bool: True if response is empty, False otherwise.
        """
        return isinstance(invoked_response, str) and invoked_response.replace(" ", "") == ""

    def _is_single_dict_response(self, response) -> bool:
        """
        Check if the response is a single dictionary.

        Args:
            response: Response to check.

        Returns:
            bool: True if response is a single dictionary, False otherwise.
        """
        return isinstance(response, list) and len(response) == 1 and isinstance(response[0], dict)

    def _identify_summarization_columns(self, df, summarization_column) -> Optional[List[str]]:
        """
        Get the summarization columns from the DataFrame.

        Args:
            df: DataFrame to check.
            summarization_column: Column for summarization.

        Returns:
            Optional[List[str]]: List of summarization columns or None.
        """
        if isinstance(summarization_column, str) and summarization_column != "":
            return [summarization_column.lower()]

        elif isinstance(summarization_column, list) and summarization_column != [""]:
            return [col.lower() for col in summarization_column]

        return None

    def _is_list_of_dicts(self, response) -> bool:
        """
        Check if the response is a list of dictionaries.

        Args:
            response: Response to check.

        Returns:
            bool: True if response is a list of dictionaries, False otherwise.
        """
        return isinstance(response, list) and isinstance(response[0], dict)

    def _process_list_of_dicts(self, response, user_input, summarization_column, message_log) -> tuple:
        """
        Handle a response that is a list of dictionaries.

        Args:
            response: Response to handle.
            user_input: User input.
            summarization_column: Column for summarization.
            message_log: Message log to update.

        Returns:
            tuple: DataFrame, updated message log, and output summary.
        """
        intermediary_df = pd.DataFrame(response)
        intermediary_df.columns = intermediary_df.columns.str.lower()

        # Log the columns present in the DataFrame
        logging.info(f"DataFrame columns: {intermediary_df.columns.tolist()}")

        summarization_column = self._identify_summarization_columns(intermediary_df, summarization_column)

        if not summarization_column:
            message_log = self._append_to_message_log(
                message_log, "No summarization column was identified.\n"
            )
            return intermediary_df, message_log, None

        # Check if the summarization column exists in the DataFrame
        if not set(summarization_column).issubset(intermediary_df.columns):
            missing_cols = set(summarization_column) - set(intermediary_df.columns)
            logging.warning(f"Missing summarization columns: {missing_cols}")
            message_log = self._append_to_message_log(
                message_log,
                f"Summarization column was identified as {summarization_column[0]} but was not found in the data\n",
            )
            return intermediary_df, message_log, None

        return self._summarize_dataframe(intermediary_df, summarization_column, user_input, message_log)

    def _setup_sql_database(self):
            """
            Initialize the SQL database connection.
            """
            logging.info("Connecting to SQL db")
            synpase_driver = "{ODBC Driver 17 for SQL Server}"

            # Keyvault Secrets
            username = os.environ.get("OPENAI_SYNAPSE_READER_USERNAME")
            synapse_server = os.environ.get("OPENAI_SYNAPSE_READER_SERVER") 
            synapse_database = os.environ.get("OPENAI_SYNAPSE_READER_DATABASE")
            synapse_password = os.environ.get("OPENAI_SYNAPSE_READER_SECRET")

            authentication = "ActiveDirectoryPassword"
            params = f"DRIVER={synpase_driver};SERVER={synapse_server};DATABASE={synapse_database};UID={username};PWD={synapse_password};AUTHENTICATION={authentication};Connection Timeout=60"
            conn_str = f"mssql+pyodbc:///?odbc_connect={params}&timeout=30"

            self.db = SQLDatabase.from_uri(
                conn_str, engine_args={"pool_recycle": 3600}, metadata=LazyReflectMetadata()
            )

    def _construct_pipeline(self, user_input: str) -> tuple:
            """
            Construct a pipeline based on user input.

            Args:
                user_input (str): User input.
                message_log (str): Message log to update.

            Returns:
                tuple: Pipeline and updated message log.
            """
            logging.info("Creating pipeline")
            response = llm_4o.invoke(self.pipeline_creator_prompt.format(user_question=user_input))

            process_flow = eval(self._strip_markdown_notation(response.content))

            return process_flow

    def _check_ambiguity(self, user_input: str, tables: dict) -> dict:
        """
        Checks the user question for ambiguity based on metadata.

        Args:
            user_input (str): The user input.
            tables (dict): The context metadata for table information.

        Returns:
            dict: A dictionary with 'Ambiguous' (bool) and 'Reason' (str) keys.
        """
        logging.info("Checking User Question for Ambiguity")
        
        # Construct the prompt using the new format enforcing valid JSON output.
        ambiguity_prompt = self.ambiguity_checker_prompt.format(user_question=user_input, context=tables)
        
        # Invoke the LLM to check ambiguity.
        response = llm_o3_mini_low.invoke(ambiguity_prompt).content.strip()
        
        try:
            ambiguity_dict = json.loads(response)
        except json.JSONDecodeError as e:
            logging.warning(f"JSON decoding failed: {e}")
            # Fallback in case of any parsing issues.
            ambiguity_dict = {"Ambiguous": False, "Reason": ""}
        
        # Optional: Print or log the parsed ambiguity dictionary.
        logging.info(f"Parsed ambiguity dict: {ambiguity_dict}")
        return ambiguity_dict
        
    def _determine_relevant_tables(self, extracted_input: str) -> list:
        """
        Identify relevant tables based on all dynamic _fields properties.
        This method collects all values from attributes ending with "_fields", concatenates them,
        and uses that combined string for the table selection prompt.
        Args:
            extracted_input (str): The user question.
        Returns:
            list: A list of relevant table names.
        """
        logging.info("Selecting Relevant Table")

        # Get all attributes ending with "_fields"
        attrs = dir(self)
        fields_props = [attr for attr in attrs if attr.endswith("_fields")]

        table_fields = []
        for prop in fields_props:
            try:
                value = getattr(self, prop)
                # If the attribute is callable (e.g., a method), call it to get the string value.
                if callable(value):
                    value = value()
                # Ensure the value is converted to a string.
                table_fields.append(str(value))
            except Exception as e:
                logging.warning(f"Error accessing {prop}: {e}")

        # Combine all field descriptions into a single string
        combined_tables = "\n".join(table_fields)

        # Create the table selection prompt, which now dumps all joined table fields.
        table_selection_prompt = self.table_selection_prompt.format(
            tables=combined_tables,
            user_question=extracted_input
        )

        response = llm_4o.invoke(table_selection_prompt)

        # Assumes that response.content returns a string that can be eval()'ed to a list.
        table_list = eval(response.content)
        return table_list
    
    def _build_relevant_prompts_dict(self, relevant_tables: list) -> dict:
        """
        Builds a dictionary from the list of relevant tables. Each key corresponds to a table name,
        and each value is a dictionary containing the dynamic prompt strings for 'fields' and 'examples'.
        For example:
            {
              "REACTIVE_METRICS": {
                 "fields": <value from reactive_metrics_fields property>,
                 "examples": <value from reactive_metrics_examples property>
              },
              ...
            }
        Args:
            relevant_tables (list): List of relevant table names (assumed in uppercase).
        Returns:
            dict: A dictionary mapping table names to their prompt strings.
        """
        prompts_dict = {}
        for table in relevant_tables:
            # Build the dynamic property names assuming they follow the format:
            # <table.lower()>_fields and <table.lower()>_examples.
            fields_prop = f"{table.lower()}_fields"
            examples_prop = f"{table.lower()}_examples"
            try:
                fields_value = getattr(self, fields_prop)
                examples_value = getattr(self, examples_prop)
                prompts_dict[table] = {
                    "fields": fields_value,
                    "examples": examples_value
                }
            except AttributeError:
                logging.warning(f"Could not find dynamic properties for table: {table}")
                continue
        return prompts_dict

    def _extract_relevant_columns(self, extracted_input: str, prompts_dict: dict) -> str:
        """
        Uses the provided prompts dictionary (built from only the relevant tables) to filter and retrieve
        relevant column descriptions.
        
        Args:
            extracted_input (str): The user query.
            prompts_dict (dict): Dictionary mapping relevant tables to their prompt strings.
                               Expected format: { table: {"fields": ..., "examples": ...} }.
        Returns:
            str: The concatenated filtered column descriptions.
        """
        logging.info(f"Extracting columns from relevant tables: {list(prompts_dict.keys())}")
        filtered_descriptions_list = []
        for table, prompt_pair in prompts_dict.items():
            full_description = prompt_pair["fields"]
            filter_prompt = self.filter_columns_prompt.format(
                user_question=extracted_input,
                col_description=full_description
            )
            filtered_response = llm_o3_mini_low.invoke(filter_prompt)  #llm_o3_mini
            filtered_descriptions_list.append(filtered_response.content.strip())

        filtered_descriptions = "\n\n".join(filtered_descriptions_list)
        return filtered_descriptions

    def _extract_relevant_examples(self, extracted_input: str, prompts_dict: dict) -> str:
        """
        Uses the provided prompts dictionary to filter and retrieve relevant SQL examples.
        
        Args:
            extracted_input (str): The user query.
            prompts_dict (dict): Dictionary mapping relevant tables to their prompt strings.
        Returns:
            str: The concatenated filtered SQL examples.
        """
        logging.info(f"Extracting examples from relevant tables: {list(prompts_dict.keys())}")
        filtered_example_list = []
        for table, prompt_pair in prompts_dict.items():
            full_examples = prompt_pair["examples"]
            filter_prompt = self.filter_examples_prompt.format(
                user_question=extracted_input,
                examples=full_examples
            )
            filtered_response = llm_o3_mini_low.invoke(filter_prompt)
            filtered_example_list.append(filtered_response.content.strip())

        filtered_examples = "\n\n".join(filtered_example_list)
        return filtered_examples

    def _generate_sql_from_question(
        self, table_names: List, process_flow: Dict, message_log: str, 
        filtered_descriptions: str, filtered_examples: str
        ) -> tuple:
        logging.info("Generating SQL Query")
        table_name_str = "{}".format(", ".join(table_names))
        message_log = self._append_to_message_log(message_log,
                        "\nRelevant Table(s):\n {}\n".format(table_name_str))
        
        if process_flow["Summarization_Component"] in ("", [""]):
            identified_question = process_flow["SQL_Component"]
        else:
            identified_question = process_flow["SQL_Component"] + " only return field {}".format(process_flow["Summarization_Component"])
        
        prompt_sql = PromptTemplate.from_template(
            template=self.sql_gen_prompt,
            partial_variables={
                "input": identified_question,
                "table_info": table_name_str,
                "col_desc": filtered_descriptions,
                "examples": filtered_examples,
                "top_k": 10000,
            }
        )
        
        chain_sql = create_sql_query_chain(llm_o3_mini, self.db, prompt=prompt_sql, k=10000)
        sql_code = chain_sql.invoke({"question": identified_question})
        
        sql_code = self._strip_markdown_notation(sql_code)
        
        return sql_code, message_log, prompt_sql

    def _execute_sql_and_retrieve_results(self, sql_code: str, message_log: str, prompt_sql: object, relevant_columns: str, relevant_examples: str) -> tuple:
        """
        Execute SQL code and retrieve results.

        Args:
            sql_code (str): SQL code to execute.
            message_log (str): Message log to update.

        Returns:
            tuple: SQL results and updated message log.
        """


        max_retries = 1
        attempt = 0
        results = None
        while attempt <= max_retries:
            logging.info("Executing SQL query")
            sql_code = re.sub(
                r"(?i)select \*", "SELECT TOP 1000 *", sql_code
            )  # To hardcode the limit on the data for now
            sql_code_message = "## SQL Code:\nThe following SQL code was created to answer the question:\n```sql\n{}\n```\n".format(
                sql_code
            )
            sql_explainer_output = (
                str(
                    llm_4o.invoke(
                        self.sql_explainer_prompt.format(
                            sql_code = sql_code.replace("[", "").replace("]", "")
                        )
                    ).content
                )
                + "\n"
            )
            message_log = self._append_to_message_log(
                message_log, sql_code_message
            )
            message_log = self._append_to_message_log(
                message_log, sql_explainer_output
            )

            
            try:
                # Capture the start time
                start_time = time.time()
                results = self.db.run(sql_code, include_columns=True)
                message_log = self._append_to_message_log(
                    message_log,
                    "#### Query Excecution Status:\n Query was excecuted without error. \n",
                )

                return results, message_log

            except Exception as e:

                # Try to get a more detailed error message
                full_exception = traceback.format_exc()
                logging.error("An exception occurred while running the query:\n{}".format(e))
                attempt += 1
                if attempt > max_retries:
                    results = '"The constructed query failed to execute after two consecutive attempts. \
                    This is likely due to either a failure to connect to the Synapse database or the user \
                    input resulting in an unexecutable SQL query. Please review the assumptions under Detail \
                    tab and consider rephrasing your question if necessary."'

                    message_log = self._append_to_message_log(
                        message_log, "#### Query Excecution Status:\n" + results + "\n"
                    )

                    return results, message_log
                
                #Error Correcting step 
                logging.warning("\n Original SQL: {}".format(sql_code))

                chain_sql = create_sql_query_chain(llm_o3_mini, self.db, prompt=prompt_sql, k=10000)
                sql_code = chain_sql.invoke(
                    {"question": self.sql_error_correction_prompt.format(
                                                                    sql_query = sql_code,
                                                                    error = full_exception,
                                                                    columns = relevant_columns, 
                                                                    examples = relevant_examples
                                                                    )}
                )
                
                sql_code = self._strip_markdown_notation(sql_code)

                logging.warning("\n Corrected SQL: {}".format(sql_code))
                
                # Capture the end time
                end_time = time.time()

                # Calculate the elapsed time
                elapsed_time = end_time - start_time
                print(f"The error correction took {elapsed_time:.4f} seconds.")

    def _summarize_dataframe(self, df, summarization_column, user_input, message_log) -> tuple:
        """
        Summarize the data in the DataFrame.

        Args:
            df: DataFrame to summarize.
            summarization_column: Column for summarization.
            user_input: User input.
            message_log: Message log to update.

        Returns:
            tuple: DataFrame, updated message log, and output summary.
        """
        df = df[~df[summarization_column[0]].str.strip().replace("", pd.NA).isna()]

        if len(df) < 20:
            message_log = self._append_to_message_log(
                message_log,
                f"Summarization column was identified as {summarization_column[0]}, but the length of the data is {len(df)}, which is too short for summarization. Skipping summarization.\n",
            )
            return df, message_log, None

        if len(df) > 5000:
            df = df.head(5000)
            message_log = self._append_to_message_log(
                message_log,
                f"Summarization column was identified as {summarization_column[0]}. The length of the data was capped at 5000.\n",
            )

        else:
            message_log = self._append_to_message_log(
                message_log,
                f"Summarization column was identified as {summarization_column[0]}. The length of the data was {len(df)}.\n",
            )
        
        logging.info("START summarizer pipeline")

        summ = Summarizer(
            df[summarization_column[0]].to_frame(),
            summarization_column[0],
            self.summarization_reduce_template.replace("{user_question}", user_input),
            self.summarization_map_template,
            user_input,
            gpt_mod="gpt-4o-mini",
        )

        output_summary = summ.get_summary()

        logging.info("END summarizer pipeline")

        return df, message_log, output_summary

    def _process_sql_to_summary_chain(self, invoked_response, user_input: str, summarization_column, message_log) -> tuple:
        """
        Handle the chain from SQL end to summarization.

        Args:
            invoked_response: Response from SQL execution.
            user_input: User input.
            summarization_column: Column for summarization.
            message_log: Message log to update.

        Returns:
            tuple: Non-summarized result, updated message log, and summarization result.
        """
        no_summarization_text = "No summarization was performed.\n"

        try:
            logging.info("Evaluating the chain output")

            # Handle empty or invalid response
            if self._is_response_empty(invoked_response):
                message_log = self._append_to_message_log(
                    message_log,
                    "The SQL query returned no results, no subsequent summarization was performed.",
                )
                return "Query returned no results.", message_log, None

            response = eval(invoked_response)
            logging.info("Response was successfully evaluated.")

            # Handle response type
            if self._is_single_dict_response(response):
                message_log = self._append_to_message_log(
                    message_log, no_summarization_text
                )
                return str(response[0]), message_log, None

            elif self._is_list_of_dicts(response):
                return self._process_list_of_dicts(response, user_input, summarization_column, message_log)

            else:
                message_log = self._append_to_message_log(
                    message_log, no_summarization_text
                )
                return response, message_log, None

        except Exception as e:
            logging.warning(
                "Warning, error occurred while parsing the string to JSON. Error details: {}".format(e)
            )
            traceback.print_exc()
            message_log = self._append_to_message_log(
                message_log, no_summarization_text
            )
            return invoked_response[0:1000], message_log, None

    def execute_full_chain(self, query: str) -> str:
        message_log = str()

        try:
            with ThreadPoolExecutor() as executor:
                future_table_list = executor.submit(self._determine_relevant_tables,query)
                future_initialize_sql = executor.submit(self._setup_sql_database)              
                future_process_flow = executor.submit(self._construct_pipeline,query)               
                
                

                # Step 1: Determine relevant tables based on the user query.
                relevant_tables  = future_table_list.result()
                logging.info(f"Determined relevant tables: {relevant_tables}")

                # Step 2: Build the prompts dictionary only for the relevant tables.
                prompts_dict = self._build_relevant_prompts_dict(relevant_tables)

                future_ambiguous = executor.submit(self._check_ambiguity, query, prompts_dict)

                future_relevant_columns = executor.submit(self._extract_relevant_columns, query, prompts_dict)
                future_filtered_examples_list = executor.submit(self._extract_relevant_examples, query, prompts_dict)
                

                # Wait for all functions to complete
                logging.info("Finishing up Threads")
                ambiguous = future_ambiguous.result()
                if ambiguous.get("Ambiguous") == True:
                    return ambiguous.get("Reason")
                

                # Retrieve final results after each future completes.
                relevant_columns = future_relevant_columns.result()
                logging.info("Finished Relevant Columns")
                relevant_examples = future_filtered_examples_list.result()
                logging.info("Finished Relevant Examples")
                process_flow = future_process_flow.result()
                logging.info("Finished Process Flow")
                future_initialize_sql.result()
                logging.info("Finished db Connection")

            
            # Step 3: Generate the SQL code using the information from the previous steps
            sql_code, message_log, prompt_sql = self._generate_sql_from_question(
                table_names=list(prompts_dict.keys()),
                process_flow=process_flow,
                message_log=message_log,
                filtered_descriptions=relevant_columns,
                filtered_examples=relevant_examples
            )
           
            # Step 4: Execute SQL Query and Return the Results
            fetched_results, message_log = self._execute_sql_and_retrieve_results(
                sql_code, message_log, prompt_sql, relevant_columns, relevant_examples
            )

            # Step 5: Summarize the data from the SQL response if appropriate
            if len(str(fetched_results)) > 3000000:
                non_summarized_result = "\nThe response size is too large. The request need to be modified to prevent memory issues."
                summarization_result = None
                message_log = self._append_to_message_log(message_log, non_summarized_result)
                non_summarized_result += "Please ask user to modify the request."
            else:
                message_log = self._append_to_message_log(
                    message_log, "\n## Summarization Step\n"
                )
                non_summarized_result, message_log, summarization_result = self._process_sql_to_summary_chain(
                    fetched_results, 
                    query, 
                    process_flow["Summarization_Component"], 
                    message_log,
                )

            details_tool_artifact = ToolArtifact(
                content=message_log, display_name="Details", tool_name=self.name
            )
            self.dispatch_tool_artifact(details_tool_artifact)

            methodology = """\n Below is the methodology used to fetch the above data. 
            Briefly summarize it in a professional plain english way for the user in your response. 
            Use markdown and make it clean and organized looking. \n {}""".format(message_log)

            # Step 6: upload data and add link for user to download
            # Check if the response is a dataframe, as opposed to a text
            if isinstance(non_summarized_result, pd.DataFrame):
                blob_url = self.upload_dataframe_to_adls(non_summarized_result)

                capped_result = non_summarized_result.head(1000).replace('\n', ' ', regex=True)
                data_tool_artifact = ToolArtifact(
                    content=capped_result.to_markdown(),
                    display_name="Data Preview",
                    tool_name=self.name,
                    url=blob_url,
                    url_display_name="Download Full Data",
                )

                self.dispatch_tool_artifact(data_tool_artifact)
                logging.info("END ETS_chatbot_pipeline")
                if summarization_result:
                    return methodology + summarization_result
                else:
                    if non_summarized_result.drop_duplicates().shape[0] > 100:
                        return "Here are the top 100 rows of the data: \n {}".format(
                            non_summarized_result.drop_duplicates().head(100).to_json(orient="records")
                            ) + methodology
                    return non_summarized_result.drop_duplicates().to_json(orient="records") + methodology
            
            logging.info("END ETS_chatbot_pipeline")

            return non_summarized_result + methodology
        except Exception as e:
            full_exception = traceback.format_exc()      
            logging.error(f"Error: {e}")
            logging.error(f"Error: {full_exception}")
            return str(full_exception)

    def _run(self, query: ToolInput) -> str:
        """
        Run the tool with the given query.

        Args:
            query (ToolInput): Input query.

        Returns:
            str: Result of the tool execution.
        """
        run = self.execute_full_chain(query)
        return run 


# Create a tool spec, passing in your prompts dictionary.
tool_spec = ETSToolSpec(
    tool_name="ets_text2sql_tool",
    tool_description="This tool generates SQL from natural language text.",
    top_k=50,
    prompts=prompts #prompt dict from prompt.py
)

# Create an instance of ETSChatBotTool
ets_text2sql_tool = ETSChatBotTool.from_tool_spec(tool_spec)