from langchain_core.prompts import PromptTemplate
from typing import Union, List, Dict, Type, Literal
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from .example_lists import (
    sql_loaded_prefix,
    loaded_examples,
    field_description,
    summarization_reduce_template,
    table_selection_system_message,
    summarization_map_template,
    pipeline_creator_prompt,
    pipeline_tool_description,
    sql_explainer_prompt,
    acs_query_index_select,
    acs_query_fields,
    acs_index_names_mapping,
    index_description,
    index_key_date_column_mapping,
    acs_vs_sql_prompt,
)
from langchain.chains.sql_database.query import create_sql_query_chain
import pandas as pd
from .summarizer import Summarizer
import datetime  # Do not remove this
import re
import traceback
from src.core.base import LamBotTool
from src.models.tool import ToolArtifact
from src.models.constants import ToolType
from src.models.base import ConfiguredBaseModel
from pydantic import BaseModel, Field
import os
import requests
import json
from .openai_config import llm_4o
from .langchain_classes import SQLDatabase, LazyReflectMetadata
from typing import Optional
from .constants import IQMS_NCE_LIVE, RPT_IQMS_8D_GRID, VW_IPLM_PROBLEM_REPORT, VW_OAI_ESCALATION_TICKETS
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
from src.models.intermediate_step import IntermediateStep


class ToolInput(BaseModel):
    """Input to the tool."""

    query: str = Field(description="User question to be processed by the tool.")


class NceToolSpec(ConfiguredBaseModel):
    tool_name: str = Field(description="Name of the tool.")
    tool_description: str = Field(description="Description of the tool.")
    top_k: int = Field(
        description="Number of records to return, unless instructed otherwise by user"
    )


tool_spec = NceToolSpec(
    tool_name="nce_text2sql_tool", tool_description=pipeline_tool_description, top_k=50
)


class NceChatBotTool(LamBotTool):
    """NceChatBotTool contains all the functions for the nce chatbot project"""

    args_schema: Type[BaseModel] = ToolInput

    db: Optional[SQLDatabase] = None

    def __init__(
        self, name: str, description: str, tool_spec: NceToolSpec, tool_type: ToolType
    ):
        super().__init__(
            name=name, description=description, tool_type=tool_type, tool_spec=tool_spec
        )

    @classmethod
    def from_tool_spec(cls, tool_spec: NceToolSpec):
        name = tool_spec.tool_name
        description = tool_spec.tool_description
        tool_type = ToolType.non_retriever_tool
        return cls(
            name=name, description=description, tool_spec=tool_spec, tool_type=tool_type
        )

    def _update_custom_message_artifact(self, message: str, update_message: str) -> str:
        return message + update_message

    def _remove_markdown_notation(self, input_string: Union[str, dict]):
        if isinstance(input_string, dict):
            input_string = str(input_string["question_json"].content)

        # Remove SQL markdown notation
        sql_pattern = re.compile(r"```sql\n(.*?)\n```", re.DOTALL)
        input_string = sql_pattern.sub(r"\1", input_string)

        # Remove JSON markdown notation
        json_pattern = re.compile(r"```json\n(.*?)\n```", re.DOTALL)
        input_string = json_pattern.sub(r"\1", input_string)

        return input_string

    def _pipeline_creator(self, user_input: str, custom_message: str):
        details_intermediate_step = IntermediateStep(
            message= "Building the pipeline..."
        )
        self.dispatch_intermediate_step(details_intermediate_step)
        response = llm_4o.invoke(pipeline_creator_prompt.format(user_question=user_input))
        pipeline = eval(self._remove_markdown_notation(response.content))

        return pipeline, custom_message

    def _chain_table_function(self, extracted_input: str, custom_message: str):
        details_intermediate_step = IntermediateStep(
            message= "Selecting relevant tables to search over..."
        )
        self.dispatch_intermediate_step(details_intermediate_step)

        table_selection_prompt = table_selection_system_message.format(
            nce_live_columns=field_description[IQMS_NCE_LIVE],
            grid_columns=field_description[RPT_IQMS_8D_GRID],
            iplm_columns=field_description[VW_IPLM_PROBLEM_REPORT],
            es_columns=field_description[VW_OAI_ESCALATION_TICKETS],
            user_question=extracted_input,
        )
        response = llm_4o.invoke(table_selection_prompt)

        table_list = eval(response.content)

        return table_list, custom_message

    def _get_sql_code_from_question_table(
        self, table_names: List, pipeline: Dict, custom_message: str
    ):
        
        table_name_str = "tables {}".format(", ".join(table_names))

        details_intermediate_step = IntermediateStep(
            message= "Generating query over tables {}...".format(table_name_str)
        )
        self.dispatch_intermediate_step(details_intermediate_step)

        custom_message = self._update_custom_message_artifact(
            custom_message,
            "The pipeline initially identified {} to be relevant to answer the user question\n".format(
                table_name_str
            ),
        )

        examples = []
        table_info = ""
        col_desc = ""

        if IQMS_NCE_LIVE not in table_names:
            table_names.append(IQMS_NCE_LIVE)

        for table_name in table_names:
            if table_name in loaded_examples:
                examples += loaded_examples[table_name]
                table_info += table_name + " ,"
                col_desc += field_description[table_name] + "\n"

        prompt_sql = FewShotPromptTemplate(
            examples=examples,
            example_prompt=PromptTemplate.from_template(
                "User input: {input}\nSQL query: {query}"
            ),
            prefix=sql_loaded_prefix,
            suffix="User input: {input}",
            input_variables=["input", "table_info", "col_desc", "top_k"],
        )

        chain_sql = create_sql_query_chain(llm_4o, self.db, prompt=prompt_sql, k=10000)

        if pipeline["Summarization_Component"] == "" or pipeline[
            "Summarization_Component"
        ] == [""]:
            identified_question = pipeline["SQL_Component"]
        else:
            identified_question = pipeline[
                "SQL_Component"
            ] + " only return field {}".format(pipeline["Summarization_Component"])

        sql_code = chain_sql.invoke(
            {
                "question": identified_question,
                "table_info": table_info,
                "col_desc": col_desc,
                "top_k": 10000,
            }
        )
        sql_code = self._remove_markdown_notation(sql_code)

        return sql_code, custom_message

    def _get_sql_results_from_sql_code(self, sql_code: str, custom_message: str):

        sql_code = re.sub(
            r"(?i)select \*", "SELECT TOP 1000 *", sql_code
        )  # To hardcode the limit on the data for now
        sql_code_message = "## SQL Code:\nThe following SQL code was created to answer the question:\n```sql\n{}\n```\n".format(
            sql_code
        )
        sql_explainer_output = (
            str(
                llm_4o.invoke(
                    sql_explainer_prompt.format(
                        sql_code.replace("[", "").replace("]", "")
                    )
                ).content
            )
            + "\n"
        )
        custom_message = self._update_custom_message_artifact(
            custom_message, sql_code_message
        )
        custom_message = self._update_custom_message_artifact(
            custom_message, sql_explainer_output
        )

        max_retries = 1
        attempt = 0
        results = None

        while attempt <= max_retries:
            try:
                details_intermediate_step = IntermediateStep(
                    message= "Executing query: {}...".format(sql_code)
                )
                self.dispatch_intermediate_step(details_intermediate_step)
                results = self.db.run(sql_code, include_columns=True)
                custom_message = self._update_custom_message_artifact(
                    custom_message,
                    "#### Query Excecution Status:\n Query was excecuted without error. \n",
                )

                return results, custom_message

            except Exception as e:
                logging.warning("Exception occurred while running the query: {}".format(e))
                attempt += 1
                if attempt > max_retries:

                    results = '"The constructed query failed to execute after two consecutive attempts. This is likely due to either a failure to connect to the Synapse database or the user input resulting in an unexecutable SQL query. Please review the assumptions under Detail tab and consider rephrasing your question if necessary."'
                    custom_message = self._update_custom_message_artifact(
                        custom_message, "#### Query Excecution Status:\n" + results + "\n"
                    )

                    return results, custom_message

    def _chain_start_to_sql_end_sql_route(
        self, user_input: str, custom_message: str = ""
    ):
        pipeline, custom_message = self._pipeline_creator(user_input, custom_message)
        table_list, custom_message = self._chain_table_function(
            pipeline["SQL_Component"], custom_message
        )
        sql_code, custom_message = self._get_sql_code_from_question_table(
            table_list, pipeline, custom_message
        )
        fetched_results, custom_message = self._get_sql_results_from_sql_code(
            sql_code, custom_message
        )

        return fetched_results, sql_code, table_list, pipeline, custom_message


    def _is_empty_response(self, invoked_response):
        return isinstance(invoked_response, str) and invoked_response.replace(" ", "") == ""


    def _is_single_dict_response(self, response):
        return isinstance(response, list) and len(response) == 1 and isinstance(response[0], dict)


    def _is_list_of_dicts(self, response):
        return isinstance(response, list) and isinstance(response[0], dict)


    def _handle_list_of_dicts(self, response, user_input, summarization_column, custom_message):
        intermediary_df = pd.DataFrame(response)
        intermediary_df.columns = intermediary_df.columns.str.lower()

        summarization_column = self._get_summarization_columns(intermediary_df, summarization_column)

        if not summarization_column:
            custom_message = self._update_custom_message_artifact(
                custom_message, "No summarization column was identified.\n"
            )
            return intermediary_df, custom_message, None

        if not set(summarization_column).issubset(intermediary_df.columns):
            custom_message = self._update_custom_message_artifact(
                custom_message,
                f"Summarization column was identified as {summarization_column[0]} but was not found in the data\n",
            )
            return intermediary_df, custom_message, None

        return self._summarize_data(intermediary_df, summarization_column, user_input, custom_message)


    def _get_summarization_columns(self, df, summarization_column):
        if isinstance(summarization_column, str) and summarization_column != "":
            return [summarization_column.lower()]

        elif isinstance(summarization_column, list) and summarization_column != [""]:
            return [col.lower() for col in summarization_column]

        return None


    def _summarize_data(self, df, summarization_column, user_input, custom_message):
        df = df[~df[summarization_column[0]].str.strip().replace("", pd.NA).isna()]

        if len(df) < 20:
            custom_message = self._update_custom_message_artifact(
                custom_message,
                f"Summarization column was identified as {summarization_column[0]}, but the length of the data is {len(df)}, which is too short for summarization. Skipping summarization.\n",
            )
            return df, custom_message, None

        if len(df) > 5000:
            df = df.head(5000)
            custom_message = self._update_custom_message_artifact(
                custom_message,
                f"Summarization column was identified as {summarization_column[0]}. The length of the data was capped at 5000.\n",
            )

        else:
            custom_message = self._update_custom_message_artifact(
                custom_message,
                f"Summarization column was identified as {summarization_column[0]}. The length of the data was {len(df)}.\n",
            )
        
        logging.info("START summarizer pipeline")
        details_intermediate_step = IntermediateStep(
            message= "Summarizing {} records...".format(len(df))
        )
        self.dispatch_intermediate_step(details_intermediate_step)
        summ = Summarizer(
            df[summarization_column[0]].to_frame(),
            summarization_column[0],
            summarization_reduce_template.replace("{user_question}", user_input),
            summarization_map_template,
            user_input,
            gpt_mod="gpt-4o-mini",
        )

        output_summary = summ.get_summary()

        logging.info("END summarizer pipeline")

        return df, custom_message, output_summary

    def _chain_sql_end_to_summarization(self, invoked_response, user_input: str, summarization_column, custom_message):
        no_summarization_text = "No summarization was performed.\n"
        details_intermediate_step = IntermediateStep(
            message= "Evaluating query output..."
        )
        self.dispatch_intermediate_step(details_intermediate_step)
        try:
            logging.info("Evaluating the chain output")

            # Handle empty or invalid response
            if self._is_empty_response(invoked_response):
                custom_message = self._update_custom_message_artifact(
                    custom_message,
                    "The SQL query returned no results, no subsequent summarization was performed.",
                )
                return "Query returned no results.", custom_message, None

            response = eval(invoked_response)
            logging.info("Response was successfully evaluated.")

            # Handle response type
            if self._is_single_dict_response(response):
                custom_message = self._update_custom_message_artifact(
                    custom_message, no_summarization_text
                )
                return str(response[0]), custom_message, None

            elif self._is_list_of_dicts(response):
                return self._handle_list_of_dicts(response, user_input, summarization_column, custom_message)

            else:
                custom_message = self._update_custom_message_artifact(
                    custom_message, no_summarization_text
                )
                return response, custom_message, None

        except Exception as e:
            logging.warning(
                "Warning, error occurred while parsing the string to JSON. Error details: {}".format(e)
            )
            traceback.print_exc()
            custom_message = self._update_custom_message_artifact(
                custom_message, no_summarization_text
            )
            return invoked_response[0:1000], custom_message, None


    def _get_acs_index(self, user_question: str):
        """get acs index name from user input"""

        index_prompt = acs_query_index_select.format(
            acs_index_names_mapping[IQMS_NCE_LIVE],
            acs_index_names_mapping[RPT_IQMS_8D_GRID],
            acs_index_names_mapping[VW_IPLM_PROBLEM_REPORT],
            acs_index_names_mapping[VW_OAI_ESCALATION_TICKETS],
            index_description[acs_index_names_mapping[IQMS_NCE_LIVE]],
            index_description[acs_index_names_mapping[RPT_IQMS_8D_GRID]],
            index_description[acs_index_names_mapping[VW_IPLM_PROBLEM_REPORT]],
            index_description[acs_index_names_mapping[VW_OAI_ESCALATION_TICKETS]],
            user_question,
        )
        response_ = llm_4o.invoke(index_prompt) 
        index_name = response_.content.strip()
        return index_name


    def _get_acs_query_params(
            self, user_question: str, selected_index: str, top_k: int = 50
    ):
        """get acs filer, fields, query from user input"""
        
        index_definition = index_description[selected_index]
        current_date = datetime.datetime.today().strftime("%Y-%m-%d")
        input_prompt = acs_query_fields.format(
            user_question, index_definition, current_date
        )
        response = llm.invoke(input_prompt)    
        acs_query_params = response.content.strip().strip("```json").strip("```")
        acs_query_params_dict = json.loads(acs_query_params)

        index_key = index_key_date_column_mapping[selected_index]["acs_key"]
        
        if "select" in acs_query_params_dict:
            if index_key not in acs_query_params_dict["select"]:
                acs_query_params_dict["select"] += ", {}".format(index_key)
        else:
            acs_query_params_dict["select"] = index_key

        acs_query_params_dict["top"] = 50

        return acs_query_params_dict



    def _query_acs(self, search_params, acs_index_name):
        """Query ACS index using the description query."""

        ACS_ENDPOINT = os.getenv("SEARCH_API_BASE")
        ACS_API_KEY = os.getenv("SEARCH_API_KEY")
        # Create the search URL
        search_url = f"{ACS_ENDPOINT}/indexes/{acs_index_name}/docs/search?api-version=2021-04-30-Preview"

        # Headers for the request
        headers = {
            "Content-Type": "application/json",
            "api-key": ACS_API_KEY
        }

        # Perform the POST request to the search API
        logging.info("Sending the POST request to the search API")

        response = requests.post(
            search_url, headers=headers, data=json.dumps(search_params)
        )
        
        if response.status_code == 200:
            search_results = response.json()
            return search_results
        else:
            logging.warning(f"Error during search: {response.status_code} - {response.text}")
            return {"Error": response.text}
        

    def _query_acs_user_input(self, user_input: str, custom_message: str):
        details_intermediate_step = IntermediateStep(
            message= "Running the search pipeline..."
        )
        self.dispatch_intermediate_step(details_intermediate_step)
        acs_index_name = self._get_acs_index(user_input)
        custom_message_index_name = "#### Overall Summary:\n To answer the question we search the Azure AI Index data. The index {} was searched to answer the user question. \n".format(
            acs_index_name
        )
        custom_message = self._update_custom_message_artifact(
            custom_message, custom_message_index_name
        )

        #----------------- Get Keywords, columns_to_select, filters ------------------------
        details_intermediate_step = IntermediateStep(
            message= "Identifying search parameters..."
        )
        self.dispatch_intermediate_step(details_intermediate_step)
        acs_query_params = self._get_acs_query_params(user_input, acs_index_name)
        
        logging.info("ACS Query Parameters: {}".format(acs_query_params))


        custom_message_acs_params = "#### ACS Parameters:\n The following search parameters were identified for the ACS search: {} \n".format(
            acs_query_params
        )
        custom_message = self._update_custom_message_artifact(
            custom_message, custom_message_acs_params
        )

        #----------------- Get final results by querying ACS------------------------
        acs_query_params = self._get_acs_query_params(user_input, acs_index_name)
        
        details_intermediate_step = IntermediateStep(
            message="Running the search query..."
            )
        self.dispatch_intermediate_step(details_intermediate_step)

        results = self._query_acs(acs_query_params, acs_index_name)

        results_value = results.get("value", None)

        if results_value == []:
            return "The search returned no results", custom_message
        elif results_value:
            return pd.DataFrame(results["value"]).drop(columns=["@search.score"], errors="ignore"), custom_message
        else:
            logging.warning(type(results.get("Error", "Unknown error.")))
            custom_message_error = "\nThe following error was encountered while retrieving the results, please modify the assumptions if needed and resubmit the results: \n{}".format(
                results.get("Error", "Unknown Error")
            )
            custom_message = self._update_custom_message_artifact(
                custom_message, custom_message_error
            )
            return custom_message_error, custom_message


    def _get_acs_vs_sql(self, user_question: str) -> Literal["ACS", "SQL"]:
        """acs or sql classifier"""

        input_prompt = acs_vs_sql_prompt.format(user_question)
        response = llm_4o.invoke(input_prompt)

        output_acs_sql = str(response.content)

        if output_acs_sql.endswith("SQL"):
            return "SQL"
        elif output_acs_sql.endswith("ACS"):
            return "ACS"
        else:
            return "SQL"

    def _initialize_sql_database(self):
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

    def _complete_chain_function(self, query: str):

        logging.info("START nce_chatbot_pipeline")
        self._initialize_sql_database()

        custom_message = str()
        
        acs_sql = self._get_acs_vs_sql(query)

        if acs_sql == "ACS":
            non_summarized_result, custom_message = self._query_acs_user_input(
                query, custom_message
            )
            summarization_result = None

        else:
            fetched_results, _, _, pipeline, custom_message = (
                self._chain_start_to_sql_end_sql_route(query, custom_message)
            )

            if len(str(fetched_results)) > 3000000:
                non_summarized_result = "\nThe response size is too large. The request need to be modified to prevent memory issues."
                summarization_result = None
                custom_message = self._update_custom_message_artifact(custom_message, non_summarized_result)
                non_summarized_result += "Please ask user to modify the request."
            else:
    
                custom_message = self._update_custom_message_artifact(
                    custom_message, "\n## Summarization Step\n"
                )
                non_summarized_result, custom_message, summarization_result = self._chain_sql_end_to_summarization(
                    fetched_results, 
                    query, 
                    pipeline["Summarization_Component"], 
                    custom_message,
                )

        details_tool_artifact = ToolArtifact(
            content=custom_message, display_name="Details", tool_name=self.name
        )
        self.dispatch_tool_artifact(details_tool_artifact)

        if isinstance(non_summarized_result, pd.DataFrame):
            blob_url = self.upload_dataframe_to_adls(non_summarized_result)

            capped_result = non_summarized_result.head(50).replace('\n', ' ', regex=True)
            data_tool_artifact = ToolArtifact(
                content=capped_result.to_markdown(),
                display_name="Data Preview",
                tool_name=self.name,
                url=blob_url,
                url_display_name="Download Full Data",
            )

            self.dispatch_tool_artifact(data_tool_artifact)
            logging.info("END nce_chatbot_pipeline")

            if summarization_result:
                return summarization_result
            else:
                if non_summarized_result.drop_duplicates().shape[0] > 5:
                    return "Here are the top 5 rows of the data: \n {}".format(
                        non_summarized_result.drop_duplicates().head(5).to_json(orient="records")
                        )
                return non_summarized_result.drop_duplicates().to_json(orient="records")
        
        logging.info("END nce_chatbot_pipeline")
        return non_summarized_result


    def _run(self, query: ToolInput) -> str:
        return self._complete_chain_function(query)

    async def _arun(self, query: ToolInput) -> str:
        return self._complete_chain_function(query)


# create an instance of NceChatBotTool
nce_tool = NceChatBotTool.from_tool_spec(tool_spec)
