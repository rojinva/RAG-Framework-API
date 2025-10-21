import ast
import json
from typing import Type, Optional, List
from pydantic import BaseModel
from src.core.base import LamBotDocument
from src.core.base import LamBotTool
from langchain_core.retrievers import BaseRetriever
from src.models import ToolType
from dotenv import load_dotenv
import pandas as pd
from src.models.tool import ToolArtifact
from src.core.tools.community.fmea_conv.abstraction.fmea_agent_tool_spec_model import FMEAToolSpec, ToolInput
from src.core.tools.community.fmea_conv.abstraction.constant import StaticData, StaticFilters
from src.core.tools.community.fmea_conv.abstraction.services import FmeaDataHandler
from concurrent.futures import ThreadPoolExecutor
import base64
from src.models.intermediate_step import IntermediateStep
from datetime import datetime
import numpy as np

load_dotenv(override=True)
from src.clients import LifespanClients
from src.models.request import MessageFile


class LamBotFMEAAgentTool(LamBotTool):
    """FMEA Agent tool."""

    args_schema: Type[BaseModel] = ToolInput
    tool_spec: FMEAToolSpec
    file_attachments: Optional[List[MessageFile]] = None

    def __init__(
        self,
        name: str,
        description: str,
        tool_spec: FMEAToolSpec,
        tool_type: ToolType,
    ):
        super().__init__(
            name=name, description=description, tool_type=tool_type, tool_spec=tool_spec
        )
        self.tool_spec = tool_spec
        
    @classmethod 
    def _get_tool_description(cls, tool_spec: FMEAToolSpec) -> str:
        """Get the tool description from the tool_description_prompt."""
        prompt_name, fallback_prompt = tool_spec.prompts["tool_description_prompt"]
        client = LifespanClients.get_instance().langfuse_manager
        tool_description_prompt = client.get_prompt(
            prompt_name=prompt_name,
            fallback_prompt=fallback_prompt
        )
        return tool_description_prompt
    
    @classmethod
    def from_tool_spec(cls, tool_spec: FMEAToolSpec):
        name = tool_spec.tool_name
        description = cls._get_tool_description(tool_spec)
        tool_type = ToolType.non_retriever_tool
        return cls(
            name=name, description=description, tool_spec=tool_spec, tool_type=tool_type
        )

    @property
    def retrievers(self) -> List[BaseRetriever]:
        """Configure and return the AzureAISearchRetriever based on the provided tool configuration."""
        return FmeaDataHandler.configure_retrievers(self.tool_spec)
    
    def _retrieve(self, query: ToolInput, filter_keyword: str):
        retrieved_lambot_documents = []
        for retriever in self.retrievers:
            retriever.azure_search_config["filter"] = f"search.ismatch('{filter_keyword}', 'metadata')"
            _retrieved_lambot_documents = retriever.invoke(query.query)
            retrieved_lambot_documents.extend(_retrieved_lambot_documents)
        return retrieved_lambot_documents
    
    def pick_relevant_fields(self, lambot_documents, fields):
        chunk_list = [ast.literal_eval(item) for item in lambot_documents]
        
        filtered_chunks = []
        for chunk in chunk_list:
            filtered_chunk = {field: chunk[field] for field in fields if field in chunk}
            filtered_chunks.append(filtered_chunk)
        
        return filtered_chunks
    
    def calculate_severity_updated(self, input_dataframe, filter_keyword):
        self.dispatch_intermediate_step(intermediate_step=IntermediateStep(message="Calculating Severity from Historical FMEAs…"))

        def process_row(row):
            query = f'{row["Potential Failure Mode"]} {row["Potential Effect(s) of Failure"]}'
            lambot_documents = self._retrieve(ToolInput(query=query), filter_keyword=filter_keyword)
            llm_contexts = [document.llm_context for document in lambot_documents if hasattr(document, StaticFilters.LLMCONTEXT)]
            fields = [StaticFilters.POTENTIALFAILUREMODE, StaticFilters.SEVERITY]
            filtered_chunks = self.pick_relevant_fields(llm_contexts, fields)
            severity_values = []
            for chunk in filtered_chunks:
                if StaticFilters.SEVERITY in chunk:
                    severity_value = chunk[StaticFilters.SEVERITY]
                    if isinstance(severity_value, (int, float)):
                        severity_values.append(int(severity_value))
                    elif isinstance(severity_value, str) and severity_value.strip():
                        try:
                            severity_values.append(int(float(severity_value)))
                        except ValueError:
                            pass
            if severity_values:
                average_severity = sum(severity_values) / len(severity_values)
            else:
                average_severity = 1
            return round(average_severity)

        with ThreadPoolExecutor() as executor:
            severity_list = list(executor.map(process_row, [row for _, row in input_dataframe.iterrows()]))

        input_dataframe["Severity (S)"] = severity_list
        return input_dataframe
    
    def map_potential_effect_of_failure(self, potential_failures_with_severity):
        self.dispatch_intermediate_step(intermediate_step=IntermediateStep(message="Mapping Potential Effect of Failures…"))
        severity_ranking = StaticData.severity_ranking
        potential_effect_of_failure = {}

        for failure, severity in potential_failures_with_severity.items():
            if severity in severity_ranking:
                potential_effect_of_failure[failure] = severity_ranking[severity]
            else:
                potential_effect_of_failure[failure] = 0

        return potential_effect_of_failure
    
    def calculate_occurrence_from_historical_fmea_parallel_updated(self, fmea_df, filter_keyword):
        self.dispatch_intermediate_step(intermediate_step=IntermediateStep(message="Calculating Occurrence…"))
        occurrence_list = []

        def process_row(row):
            query = f"{row[StaticFilters.POTENTIALCUASEOFMECHANISM]} {row[StaticFilters.DESIGNPREVENTION]}"
            lambot_documents = self._retrieve(ToolInput(query=query), filter_keyword=filter_keyword)
            llm_contexts = [document.llm_context for document in lambot_documents if hasattr(document, StaticFilters.LLMCONTEXT)]

            fields = [StaticFilters.POTENTIALCUASEOFMECHANISM, 
                    StaticFilters.DESIGNPREVENTION, 
                    StaticFilters.OCCURRENCE]
            filtered_chunks = self.pick_relevant_fields(llm_contexts, fields)
            sorted_chunks = sorted(filtered_chunks, key=lambda x: float(x.get(StaticFilters.OCCURRENCE, 0) or 0), reverse=True)
            sorted_chunks = sorted_chunks[0:5]

            occurrence_values = []
            for chunk in sorted_chunks:
                if StaticFilters.OCCURRENCE in chunk:
                    occurrence_value = chunk[StaticFilters.OCCURRENCE]
                    if isinstance(occurrence_value, (int, float)) and occurrence_value > 0:
                        occurrence_values.append(float(occurrence_value))
                    elif isinstance(occurrence_value, str) and occurrence_value.strip():
                        try:
                            occurrence_value_float = float(occurrence_value)
                            if occurrence_value_float > 0:
                                occurrence_values.append(occurrence_value_float)
                        except ValueError:
                            pass

            if occurrence_values:
                average_occurrence = sum(occurrence_values) / len(occurrence_values)
            else:
                average_occurrence = 1
            return round(average_occurrence)

        with ThreadPoolExecutor() as executor:
            occurrence_list = list(executor.map(process_row, [row for _, row in fmea_df.iterrows()]))

        fmea_df[StaticFilters.OCCURRENCE] = occurrence_list
        return fmea_df
    
    def map_class_from_serverity_and_occurence(self, occurence_df):
        self.dispatch_intermediate_step(intermediate_step=IntermediateStep(message="Mapping Class…"))  
        occurence_df[StaticFilters.CLASS] = 'x'

        for index, row in occurence_df.iterrows():
            severity = row[StaticFilters.SEVERITY]
            occurrence = row[StaticFilters.OCCURRENCE]
                
            if severity >= 8 and occurrence >= 2:
                occurence_df.at[index, StaticFilters.CLASS] = 'I'
            elif severity >= 5 and occurrence >= 4:
                occurence_df.at[index, StaticFilters.CLASS] = 'II'
            elif severity >= 5 and severity <= 8 and occurrence == 3:
                occurence_df.at[index, StaticFilters.CLASS] = 'III'
            elif severity >= 2 and severity <= 4 and occurrence >= 4:
                occurence_df.at[index, StaticFilters.CLASS] = 'III'
            else:
                occurence_df.at[index, StaticFilters.CLASS] = 'x'

        return occurence_df
    
    def calculate_detection_and_rpn_score_parallel_updated(self, fmea_df, filter_keyword):
        self.dispatch_intermediate_step(intermediate_step=IntermediateStep(message="Calculating Detection and RPN Score…"))  
        detection_values = []

        def process_row(row):
            potential_cause_of_failure = row[StaticFilters.POTENTIALCUASEOFMECHANISM]
            current_detection_design = row[StaticFilters.DESIGNCONTROL]
            query = f"{potential_cause_of_failure} {current_detection_design}"
            lambot_documents = self._retrieve(ToolInput(query=query), filter_keyword=filter_keyword)
            llm_contexts = [document.llm_context for document in lambot_documents if hasattr(document, StaticFilters.LLMCONTEXT)]

            fields = [StaticFilters.POTENTIALCUASEOFMECHANISM, 
                    StaticFilters.DESIGNCONTROL, 
                    StaticFilters.DETECTION]
            filtered_chunks = self.pick_relevant_fields(llm_contexts, fields)
            sorted_chunks = sorted(filtered_chunks, key=lambda x: float(x.get(StaticFilters.DETECTION, 0) or 1), reverse=True)
            sorted_chunks = sorted_chunks[0:5]

            detection_values_list = []
            for chunk in sorted_chunks:
                if StaticFilters.DETECTION in chunk:
                    detection_value = chunk[StaticFilters.DETECTION]
                    if isinstance(detection_value, (int, float)):
                        detection_values_list.append(int(detection_value))
                    elif isinstance(detection_value, str) and detection_value.strip():
                        try:
                            detection_values_list.append(int(float(detection_value)))
                        except ValueError:
                            pass

            if detection_values_list:
                average_detection = sum(detection_values_list) / len(detection_values_list)
            else:
                average_detection = 1

            return round(average_detection)

        with ThreadPoolExecutor() as executor:
            detection_values = list(executor.map(process_row, [row for _, row in fmea_df.iterrows()]))

        fmea_df[StaticFilters.DETECTION] = detection_values

        if StaticFilters.SEVERITY in fmea_df.columns and StaticFilters.OCCURRENCE in fmea_df.columns:
            fmea_df[StaticFilters.RPN] = fmea_df[StaticFilters.SEVERITY] * fmea_df[StaticFilters.OCCURRENCE] * fmea_df[StaticFilters.DETECTION]
        else:
            fmea_df[StaticFilters.RPN] = StaticFilters.REQUIREDFIELD

        return fmea_df
    
    def calculate_rpn(self, fmea_df):
        self.dispatch_intermediate_step(intermediate_step=IntermediateStep(message="Calculating RPN Score…"))  

        if StaticFilters.SEVERITY in fmea_df.columns and StaticFilters.OCCURRENCE in fmea_df.columns and StaticFilters.DETECTION in fmea_df.columns:
            try:
                fmea_df[StaticFilters.SEVERITY] = fmea_df[StaticFilters.SEVERITY].apply(lambda x: float(x) if str(x).strip().replace('.', '', 1).isdigit() else 1)
                fmea_df[StaticFilters.OCCURRENCE] = fmea_df[StaticFilters.OCCURRENCE].apply(lambda x: float(x) if str(x).strip().replace('.', '', 1).isdigit() else 1)
                fmea_df[StaticFilters.DETECTION] = fmea_df[StaticFilters.DETECTION].apply(lambda x: float(x) if str(x).strip().replace('.', '', 1).isdigit() else 1)
                fmea_df[StaticFilters.RPN] = fmea_df[StaticFilters.SEVERITY] * fmea_df[StaticFilters.OCCURRENCE] * fmea_df[StaticFilters.DETECTION]
            except Exception as e:
                fmea_df[StaticFilters.RPN] = f"Error: {str(e)}"
        else:
            fmea_df[StaticFilters.RPN] = StaticFilters.REQUIREDFIELD

        return fmea_df

    def clean_fmea(self, df, filter_keyword):
        self.dispatch_intermediate_step(intermediate_step=IntermediateStep(message="Formating Output and Generating Final FMEA Template…"))  
        df[StaticFilters.OCCURRENCE] = np.where(
            df[StaticFilters.DESIGNPREVENTION] == "none", 
            10,
            np.where(
                df[StaticFilters.DESIGNPREVENTION] == "", 
                np.nan,
                df[StaticFilters.OCCURRENCE]
            )
        )
       
        df[StaticFilters.DETECTION] = np.where(
            df[StaticFilters.DESIGNCONTROL] == "none", 
            10,
            np.where(
                df[StaticFilters.DESIGNCONTROL] == "", 
                np.nan,
                df[StaticFilters.DETECTION]
            )
        )
        
        df[StaticFilters.CLASS] = np.where(
            df[StaticFilters.OCCURRENCE].isna(), 
            "",
            df[StaticFilters.CLASS]
        )

        df[StaticFilters.RPN] = df[StaticFilters.SEVERITY] * df[StaticFilters.OCCURRENCE] * df[StaticFilters.DETECTION]
        df.loc[
            ~df[StaticFilters.CLASS].isin(["I", "II"]) | (df[StaticFilters.RPN] < 125), 
            StaticFilters.RECOMMENDEDCORRECTIVEACTION
        ] = ""
        
        fields_to_clear = [
            StaticFilters.SEVERITY, 
            StaticFilters.POTENTIALCUASEOFMECHANISM, 
            StaticFilters.FAILURECATEGORY, 
            StaticFilters.DESIGNPREVENTION, 
            StaticFilters.DESIGNCONTROL, 
            StaticFilters.OCCURRENCE, 
            StaticFilters.CLASS, 
            StaticFilters.DETECTION, 
            StaticFilters.RPN,
            StaticFilters.RECOMMENDEDCORRECTIVEACTION
        ]
        df.loc[df[StaticFilters.POTENTIALCUASEOFMECHANISM] == "None", fields_to_clear] = ""
        
        column_order = [
            StaticFilters.ITMEFUNCTION, StaticFilters.POTENTIALFAILUREMODE, StaticFilters.POTENTIALEFFECTOFFAILURE, StaticFilters.SEVERITY, 
            StaticFilters.POTENTIALCUASEOFMECHANISM, StaticFilters.FAILURECATEGORY, 
            StaticFilters.DESIGNPREVENTION, StaticFilters.OCCURRENCE, 
            StaticFilters.CLASS, StaticFilters.DESIGNCONTROL, 
            StaticFilters.DETECTION, StaticFilters.RPN, StaticFilters.RECOMMENDEDCORRECTIVEACTION
        ]
        df = df[column_order]
        
        new_fields = [StaticFilters.OWNER, StaticFilters.TARGETCOMPLETIONDATE, StaticFilters.ACTIONTAKEN, 
                    StaticFilters.PASEVERITY, StaticFilters.PAOCCURRENCE, StaticFilters.PADETECTION, StaticFilters.PARPN]
        for field in new_fields:
            df[field] = ""
        
        df[StaticFilters.SERIALNUMBER] = range(1, len(df) + 1)
        df[StaticFilters.STARTDATE] = datetime.now().strftime("%Y-%m-%d")

        df = df[[StaticFilters.SERIALNUMBER, StaticFilters.STARTDATE] + [col for col in df.columns if col not in [StaticFilters.SERIALNUMBER, StaticFilters.STARTDATE]]]
        
        blank_row_1 = pd.DataFrame({col: [""] for col in df.columns})
        blank_row_2 = pd.DataFrame({col: [""] for col in df.columns})
        
        blank_row_1.at[0, StaticFilters.POTENTIALFAILUREMODE] = "Title"
        blank_row_1.at[0, StaticFilters.POTENTIALEFFECTOFFAILURE] = filter_keyword
        blank_row_1.at[0, StaticFilters.SEVERITY] = "Description"
        blank_row_1.at[0, StaticFilters.DESIGNCONTROL] = "Requirements Document"
        blank_row_1.at[0, StaticFilters.OWNER] = "Created by"
        blank_row_1.at[0, StaticFilters.PADETECTION] = "Rev."
        
        blank_row_2.at[0, StaticFilters.OWNER] = "Date Created"
        blank_row_2.at[0, StaticFilters.TARGETCOMPLETIONDATE] = datetime.now().strftime("%Y-%m-%d")
        blank_row_2.at[0, StaticFilters.PADETECTION] = "Last Update"
        blank_row_2.at[0, StaticFilters.PARPN] = datetime.now().strftime("%Y-%m-%d")
        
        column_headers = pd.DataFrame([df.columns], columns=df.columns)
        
        df = pd.concat([blank_row_1, blank_row_2, column_headers, df], ignore_index=True)

        df =  df.drop(df.index[2])
                
        return df

    @staticmethod
    def convert_llm_contexts_to_string(lambot_documents: List[LamBotDocument]) -> str:
        # @TODO: Add converting each llm_context to strings and then return the following statement.
        return "\n".join([document.llm_context for document in lambot_documents])

    def _create_context_hardcoded(self, prompt_type: str, list_of_strings):
        """Create context from retrieved documents or use query_generation_prompt directly."""
        item_function_prompt = StaticData.ITEM_FUNCTION_PROMPT
        potential_failure_mode_prompt = StaticData.POTENTIAL_FAILURE_MODE_PROMPT
        
        if prompt_type == "item_function_prompt":
            prompt = item_function_prompt
        elif prompt_type == "potential_failure_mode_prompt":
            prompt = potential_failure_mode_prompt
        else:
            raise ValueError(f"Unknown prompt type: {prompt_type}")
        context = prompt + f'{list_of_strings}'
        return context
    
    def _create_context_updated(self, prompt_type: str, lambot_documents, potential_failure_mode=None):
        """Create context from retrieved documents or use query_generation_prompt directly."""
        potential_cause_of_failure_prompt = StaticData.POTENTIAL_CAUSE_OF_FAILURE_PROMPT
        
        recommended_corrective_action_prompt = StaticData.RECOMMENDED_CORRECTIVE_ACTION_PROMPT
                                
        if prompt_type == "potential_cause_of_failure_prompt":
            prompt = potential_cause_of_failure_prompt
        elif prompt_type == "recommended_corrective_action_prompt":
            prompt = recommended_corrective_action_prompt
        else:
            raise ValueError(f"Unknown prompt type: {prompt_type}")
        
        context = f'{lambot_documents}' + prompt + potential_failure_mode
        return context

    def generate_item_functions(self, design_requirements):
        context = self._create_context_hardcoded("item_function_prompt", design_requirements)
        item_function_list = FmeaDataHandler.generate_output_with_llm_call(context)
        return item_function_list

    def generate_potential_failure_modes(self, item_function_list):
        context = self._create_context_hardcoded("potential_failure_mode_prompt", item_function_list)
        potential_failure_mode_list = FmeaDataHandler.generate_output_with_llm_call(context)
        return potential_failure_mode_list

    def generate_potential_causes_of_failures(self, context_documents, potential_failure_mode):
        context = self._create_context_updated("potential_cause_of_failure_prompt", context_documents, potential_failure_mode)
        potential_causes_of_failures_list = FmeaDataHandler.generate_output_with_llm_call(context)
        return potential_causes_of_failures_list
    
    def generate_recommended_corrective_action(self, context_documents, line_items):
        context = self._create_context_updated("recommended_corrective_action_prompt", context_documents, line_items)
        potential_causes_of_failures_list = FmeaDataHandler.generate_output_with_llm_call(context)
        return potential_causes_of_failures_list
    
    def process_recommended_corrective_action(self, df, filter_keyword):
        self.dispatch_intermediate_step(intermediate_step=IntermediateStep(message="Generating Recommended Corrective Actions…"))
        df[StaticFilters.RPN] = pd.to_numeric(df[StaticFilters.RPN], errors='coerce')
        filter_df = df[((df[StaticFilters.CLASS].isin(["I", "II"])) | (df[StaticFilters.RPN] >= 125)) &
                    ((df[StaticFilters.RECOMMENDEDCORRECTIVEACTION] == "") | (df[StaticFilters.RECOMMENDEDCORRECTIVEACTION].isnull()))]
        
        def process_row(row):
            query = f"{row[StaticFilters.POTENTIALFAILUREMODE]} {row[StaticFilters.POTENTIALCUASEOFMECHANISM]} {row[StaticFilters.DESIGNPREVENTION]} {row[StaticFilters.DESIGNCONTROL]}"
            lambot_documents = self._retrieve(ToolInput(query=query), filter_keyword=filter_keyword)
            llm_contexts = [document.llm_context for document in lambot_documents if hasattr(document, StaticFilters.LLMCONTEXT)]
            
            fields = [StaticFilters.POTENTIALFAILUREMODE, StaticFilters.POTENTIALCUASEOFMECHANISM,
                    StaticFilters.DESIGNPREVENTION, StaticFilters.DESIGNCONTROL, 
                    StaticFilters.RECOMMENDEDCORRECTIVEACTION, StaticFilters.RPN]
            
            filtered_chunks = self.pick_relevant_fields(llm_contexts, fields)
            
            sorted_chunks = sorted(filtered_chunks, key=lambda x: float(x.get(StaticFilters.RPN, 0) or 0), reverse=True)
            sorted_chunks = sorted_chunks[0:15]
            
            recommended_corrective_action = self.generate_recommended_corrective_action(sorted_chunks, query)
            recommended_corrective_action = recommended_corrective_action.content
            
            return row.name, recommended_corrective_action

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(process_row, row) for _, row in filter_df.iterrows()]
            
            for future in futures:
                index, recommended_corrective_action = future.result()
                df.at[index, StaticFilters.RECOMMENDEDCORRECTIVEACTION] = recommended_corrective_action
        
        df[StaticFilters.RPN] = df[StaticFilters.RPN].fillna("")
                
        return df
    
    def generate_fmea_template_parallel(self, design_requirements, filter_keyword):
        item_functions = self.generate_item_functions(design_requirements)
        item_functions = eval(item_functions.content)
        
        potential_failure_modes = self.generate_potential_failure_modes(item_functions)
        potential_failure_modes = eval(potential_failure_modes.content)
        
        fields = [StaticFilters.POTENTIALFAILUREMODE, StaticFilters.POTENTIALEFFECTOFFAILURE, StaticFilters.POTENTIALCUASEOFMECHANISM, StaticFilters.FAILURECATEGORY, 
                StaticFilters.DESIGNPREVENTION, StaticFilters.OCCURRENCE,
                StaticFilters.DESIGNCONTROL, StaticFilters.DETECTION, StaticFilters.RECOMMENDEDCORRECTIVEACTION]
        rows = []

        def process_failure(item_function, potential_failure_mode):
            try:
                query = f'{potential_failure_mode}'
                lambot_documents = self._retrieve(ToolInput(query=query), filter_keyword=filter_keyword)
                llm_contexts = [document.llm_context for document in lambot_documents if hasattr(document, StaticFilters.LLMCONTEXT)]
                context_documents = self.pick_relevant_fields(llm_contexts, fields)
                filtered_chunks = sorted(context_documents, key=lambda x: (float(x.get(StaticFilters.OCCURRENCE, 0) or 0), float(x.get(StaticFilters.DETECTION, 0) or 0)), reverse=True)
                filtered_chunks = filtered_chunks[0:30]
                potential_failures = self.generate_potential_causes_of_failures(filtered_chunks, potential_failure_mode)
                potential_failures = potential_failures.content

                if potential_failures.startswith("```json"):
                    potential_cause_of_failures = potential_failures[len("```json"):].strip()
                elif potential_failures.startswith("```"):
                    potential_cause_of_failures = potential_failures[len("```"):].strip()
                potential_cause_of_failures = potential_cause_of_failures.rstrip("```").strip()
                potential_cause_of_failures = json.loads(potential_cause_of_failures)
                
                row_data = []
                for cause in potential_cause_of_failures:    
                    row_data.append({
                        StaticFilters.ITMEFUNCTION: item_function,
                        StaticFilters.POTENTIALFAILUREMODE: potential_failure_mode,
                        StaticFilters.POTENTIALEFFECTOFFAILURE: cause.get(StaticFilters.POTENTIALEFFECTOFFAILURE, None),
                        StaticFilters.POTENTIALCUASEOFMECHANISM: cause.get(StaticFilters.POTENTIALCUASEOFMECHANISM, None),
                        StaticFilters.FAILURECATEGORY: cause.get(StaticFilters.FAILURECATEGORY, None),
                        StaticFilters.DESIGNPREVENTION: cause.get(StaticFilters.DESIGNPREVENTION, None),
                        StaticFilters.DESIGNCONTROL: cause.get(StaticFilters.DESIGNCONTROL, None),
                        StaticFilters.RECOMMENDEDCORRECTIVEACTION: cause.get(StaticFilters.RECOMMENDEDCORRECTIVEACTION, None)
                    })
                return row_data
            except Exception as e:
                print(f"Error processing {potential_failure_mode}: {e}")
                return []

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(process_failure, item_function, potential_failure_mode) 
                    for item_function, potential_failure_mode in zip(item_functions, potential_failure_modes)]
            
            for future in futures:
                rows.extend(future.result())

        df = pd.DataFrame(rows)
        return df
    
    def process_fmea_results(self, design_requirements, filter_keyword, file_name):
        self.dispatch_intermediate_step(intermediate_step=IntermediateStep(message="FMEA generation in process, please wait and do not refresh the browser as it might take few mints…"))
        try:
            fmea_df = self.generate_fmea_template_parallel(design_requirements, filter_keyword)
        except Exception as e:
            error_message = f"Failed to Inital FMEA fields from Historical FMEA: {str(e)}"
            error_artifact = ToolArtifact(
                content=error_message,
                display_name="Error",
                tool_name="fmea_creation_agent_tool",
                url=None,
                url_display_name=None,
            )
            self.dispatch_tool_artifact(error_artifact)
            raise ValueError(error_message)
        
        try:
            severity_df = self.calculate_severity_updated(fmea_df, filter_keyword)
        except Exception as e:
            error_message = f"Failed to calculate severity from historical FMEA: {str(e)}"
            error_artifact = ToolArtifact(
                content=error_message,
                display_name="Error",
                tool_name="fmea_creation_agent_tool",
                url=None,
                url_display_name=None,
            )
            self.dispatch_tool_artifact(error_artifact)
            raise ValueError(error_message)
        
        try:
            occurrence_df = self.calculate_occurrence_from_historical_fmea_parallel_updated(severity_df, filter_keyword)
            class_df = self.map_class_from_serverity_and_occurence(occurrence_df)
        except Exception as e:
            error_message = f"Failed to map class from severity and occurrence: {str(e)}"
            error_artifact = ToolArtifact(
                content=error_message,
                display_name="Error",
                tool_name="fmea_creation_agent_tool",
                url=None,
                url_display_name=None,
            )
            self.dispatch_tool_artifact(error_artifact)
            raise ValueError(error_message)
        
        try:
            df = self.calculate_detection_and_rpn_score_parallel_updated(class_df, filter_keyword)
        except Exception as e:
            error_message = f"Failed to calculate RPN score: {str(e)}"
            error_artifact = ToolArtifact(
                content=error_message,
                display_name="Error",
                tool_name="fmea_creation_agent_tool",
                url=None,
                url_display_name=None,
            )
            self.dispatch_tool_artifact(error_artifact)
            raise ValueError(error_message)
        
        try:
            clean_df = self.clean_fmea(df, filter_keyword)
            df = self.process_recommended_corrective_action(clean_df, filter_keyword)
        except Exception as e:
            error_message = f"Failed to clean FMEA data: {str(e)}"
            error_artifact = ToolArtifact(
                content=error_message,
                display_name="Error",
                tool_name="fmea_creation_agent_tool",
                url=None,
                url_display_name=None,
            )
            self.dispatch_tool_artifact(error_artifact)
            raise ValueError(error_message)
        
        try:
            blob_url = self.upload_dataframe_to_adls(dataframe=df, file_name=file_name)
        except Exception as e:
            error_message = f"Failed to upload FMEA template to ADLS: {str(e)}"
            error_artifact = ToolArtifact(
                content=error_message,
                display_name="Error",
                tool_name="fmea_creation_agent_tool",
                url=None,
                url_display_name=None,
            )
            self.dispatch_tool_artifact(error_artifact)
            raise ValueError(error_message)
        
        fmea_tool_artifact = ToolArtifact(
            content=df.iloc[2:10].to_markdown(),
            display_name="FMEA", 
            tool_name="fmea_creation_agent_tool",
            url=blob_url,
            url_display_name="Download FMEA Template"
        )
        
        self.dispatch_tool_artifact(fmea_tool_artifact)
            
    def _run(self, query: ToolInput) -> str:
        """Run the retriever tool synchronously."""
        self.dispatch_intermediate_step(intermediate_step=IntermediateStep(message="Your file uploaded successfully, analysing the design requirement…"))
        pptx_bytes = self.file_attachments[0].value
        filter_keyword, part_value, pg_name, bu_name, tool, design_requirements, *_  = FmeaDataHandler.create_design_requirements_from_pptx_bytes(base64.b64decode(pptx_bytes))
        common_item_functions = StaticData.common_item_functions
        design_requirements.extend(common_item_functions)
        file_name = f"{pg_name}_{bu_name}_FMEA_of_{tool}_{filter_keyword}_{part_value}_{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}"
        self.process_fmea_results(design_requirements, filter_keyword, file_name)
        tool_output = "Please refer below link to download FMEA"
        return tool_output