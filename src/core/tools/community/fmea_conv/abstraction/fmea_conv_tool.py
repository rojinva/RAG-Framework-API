import os
import ast
import json
import pyodbc
import asyncio
from typing import Dict, Type, Optional, Union, List, Tuple, Callable
from pydantic import BaseModel, Field
from src.core.base import LamBotDocument
from src.core.base import LamBotTool
from langchain_core.retrievers import BaseRetriever
from src.models import ToolType
from dotenv import load_dotenv
import pandas as pd
from src.models.tool import ToolArtifact
from src.core.tools.community.fmea_conv.abstraction.fmea_agent_tool_spec_model import FMEAToolSpec, ToolInput, FMEARetrieverSpec
from src.core.tools.community.fmea_conv.abstraction.constant import StaticData, StaticFilters
from src.core.tools.community.fmea_conv.abstraction.services import FmeaDataHandler
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
import base64
import math
from pptx import Presentation
from src.models.intermediate_step import IntermediateStep
from datetime import datetime

load_dotenv(override=True)
from src.clients import LifespanClients
from src.models.request import MessageFile
from src.models.constants import IntakeItem

class LamBotFMEAConvTool(LamBotTool):
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
            name=name, description=description, tool_type=tool_type, tool_spec=tool_spec, allowed_intakes=[IntakeItem.CONVERSATION_HISTORY]
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
    
    def _retrieve(self, query: ToolInput, filter_keyword: Optional[str] = None):
        retrieved_lambot_documents = []
        for retriever in self.retrievers:
            if retriever == "historical_fmea_retriever":
                if filter_keyword is not None:
                    retriever.azure_search_config[StaticFilters.FILTER] = f"search.ismatch('{filter_keyword}', 'metadata')"
                else:
                    retriever.azure_search_config[StaticFilters.FILTER] = ""
            else:
                retriever.azure_search_config[StaticFilters.FILTER] = ""
            _retrieved_lambot_documents = retriever.invoke(query.query)
            retrieved_lambot_documents.extend(_retrieved_lambot_documents)
        return retrieved_lambot_documents
    
    @staticmethod
    def convert_llm_contexts_to_string(lambot_documents: List[LamBotDocument]) -> str:
        # @TODO: Add converting each llm_context to strings and then return the following statement.
        return "\n".join([document.llm_context for document in lambot_documents])

    def _create_context_hardcoded(self, prompt_type: str, list_of_strings, query=None, conversation_history=None):
        """Create context from retrieved documents or use query_generation_prompt directly."""
        item_function_prompt = StaticData.ITEM_FUNCTION_PROMPT
        potential_failure_mode_prompt = StaticData.POTENTIAL_FAILURE_MODE_PROMPT
        filter_potential_failure_modes = StaticData.FILTER_POTENTIAL_FAILURE_MODE
        answer_generic_questions = StaticData.ANSWER_GENERIC_QUESTION                       
        
        if prompt_type == "item_function_prompt":
            prompt = item_function_prompt
        elif prompt_type == "potential_failure_mode_prompt":
            prompt = potential_failure_mode_prompt
        elif prompt_type == "filter_potential_failure_modes":
            prompt = filter_potential_failure_modes
        elif prompt_type == "answer_generic_questions":
            prompt = answer_generic_questions
        else:
            return {"status": "error", "message": f"Unknown prompt type: {prompt_type}"}
        context = prompt + f'{query}' + f'{list_of_strings}' + f'{conversation_history}'
        return context
    
    def _create_context_missing_line_items(self, prompt_type: str, query, lambot_documents, potential_failure_mode=None, 
                                fmea_chunk=None, existing_item_functions=None, boundary_conditions_list=None, interaction_type_list=None, conversation_history=None, root_cause=None):
        generate_missing_line_items_prompt = StaticData.GENERATE_MISSING_LINE_ITEMS

        if prompt_type != "generate_missing_line_items_prompt":
            return {"status": "error", "message": f"Unknown prompt type: {prompt_type}"}

        context = (
            f"Conversation History :\n{conversation_history}\n\n"
            f"User Query:\n{query}\n\n"
            f"Context retrieved from index:\n{lambot_documents}\n\n"
            f"Manually filled FMEA for the given Potential Failure Mode:\n{fmea_chunk}\n\n"
            f"Existing Item Functions:\n{existing_item_functions}\n\n"
            f"Boundary Conditions, and Interaction Types:\n" + "\n".join(
            [f"Boundary Condition: {boundary}, Interaction Type: {interaction}" 
             for boundary, interaction in zip(boundary_conditions_list, interaction_type_list)]) + "\n\n"
            f"Pre-defined 'Potential Effect(s) of Failure' relevant to Potential Failure Mode:\n{root_cause}\n\n"
            f"{generate_missing_line_items_prompt}{potential_failure_mode}"
        )

        return context
    
    def _create_context_fix_line_items(self, prompt_type: str, query, lambot_documents, potential_failure_mode=None, 
                                    ai_fmea_chunk=None, expected_failure_modes=None,
                                    boundary_conditions_list=None, interaction_type_list=None, conversation_history=None):
        fix_line_items_prompt = StaticData.IMPROVE_LINE_ITEMS

        if prompt_type != "fix_line_items_prompt":
            return {"status": "error", "message": f"Unknown prompt type: {prompt_type}"}

        context = (
            f"Conversation History :\n{conversation_history}\n\n"
            f"User feedback to improve the new generated line items :\n{query}\n\n"
            f"Context retrieved from index:\n{lambot_documents}\n\n"
            f"Previously AI-generated FMEA for the given Potential Failure Mode:\n{ai_fmea_chunk}\n\n"
            f"Expected Potential Failure Modes, their respective Boundary Conditions, and Interaction Types:\n" + "\n".join(
                [f"Potential Failure Mode: {mode}, Boundary Condition: {boundary}, Interaction Type: {interaction}" 
                for mode, boundary, interaction in zip(expected_failure_modes, boundary_conditions_list, interaction_type_list)]) + "\n\n"
            f"{fix_line_items_prompt}{potential_failure_mode}"
        )

        return context
    
    def _create_root_cause_based_line_items(self, prompt_type: str, query, lambot_documents, 
                                boundary_conditions_list=None, interaction_type_list=None, potential_failure_mode=None, existing_item_functions=None, root_cause=None, item_fun=None):
        generate_root_cause_based_items_prompt = StaticData.GENERATE_ROOT_CAUSES_BASED_ITEMS

        if prompt_type != "generate_root_cause_based_items_prompt":
            return {"status": "error", "message": f"Unknown prompt type: {prompt_type}"}

        context = (
            f"User Query:\n{query}\n\n"
            f"Context retrieved from index:\n{lambot_documents}\n\n"
            f"Existing Item Functions list:\n{existing_item_functions}\n\n"
            f"Expected Potential Failure Modes, their respective Boundary Conditions, and Interaction Types:\n" + "\n".join(
            [f"Potential Failure Mode: {failure_mode}, Boundary Condition: {boundary}, Interaction Type: {interaction}" 
             for failure_mode, boundary, interaction in zip(potential_failure_mode, boundary_conditions_list, interaction_type_list)]) + "\n\n"
            f"Must to include 'Potential Cause(s) / Mechanism(s) of Failure':\n{root_cause}\n\n"
            f"Given 'Item Function':\n{item_fun}\n\n"
            f"{generate_root_cause_based_items_prompt}{potential_failure_mode}"
        )

        return context

    def generate_item_functions(self, design_requirements):
        context = self._create_context_hardcoded("item_function_prompt", design_requirements)
        item_function_list = FmeaDataHandler.generate_output_with_llm_call(context)
        return item_function_list

    def generate_potential_failure_modes(self, item_function_list):
        context = self._create_context_hardcoded("potential_failure_mode_prompt", item_function_list)
        potential_failure_mode_list = FmeaDataHandler.generate_output_with_llm_call(context)
        return potential_failure_mode_list
    
    def answer_generic_questions(self, llm_context, query, conversation_history):
        context = self._create_context_hardcoded("answer_generic_questions", llm_context, query, conversation_history)
        generic_response = FmeaDataHandler.generate_output_with_llm_call(context)
        return generic_response
    
    def filter_potential_failure_modes(self, ai_potential_failure_modes, query):
        context = self._create_context_hardcoded("filter_potential_failure_modes", ai_potential_failure_modes, query)
        ai_potential_failure_mode_list = FmeaDataHandler.generate_output_with_llm_call(context)
        return ai_potential_failure_mode_list
    
    def add_component_name(self, root_causes_mapping_list, design_requirements=None, boundary_conditions_list=None, interaction_type_list=None):
        if root_causes_mapping_list is None:
            return []
        context = (f"{design_requirements}\n{boundary_conditions_list}\n{interaction_type_list}\n{StaticData.ADD_COMPONENT_NAME}\n{root_causes_mapping_list}"
        )
        try:
            raw_root_causes = FmeaDataHandler.generate_output_with_llm_call(context)
        except Exception as e:
            return {"status": "error", "message": f"Failed to add component name: {e}"}
        return raw_root_causes
    
    def generate_missing_line_items(self, query, context_documents, potential_failure_mode=None, fmea_chunk=None, 
                                    existing_item_functions=None,
                                    boundary_conditions_list=None, interaction_type_list=None, conversation_history=None, root_cause=None):
        context = self._create_context_missing_line_items('generate_missing_line_items_prompt', query, context_documents, potential_failure_mode, fmea_chunk, 
                                                        existing_item_functions, boundary_conditions_list, interaction_type_list, conversation_history, root_cause)
        missing_line_items_list = FmeaDataHandler.generate_output_with_llm_call(context)
        return missing_line_items_list
    
    def generate_improved_line_items(self, query, context_documents, potential_failure_mode=None, ai_fmea_chunk=None, 
                                    expected_failure_modes=None, 
                                    boundary_conditions_list=None, interaction_type_list=None, conversation_history=None):
        context = self._create_context_fix_line_items('fix_line_items_prompt', query, context_documents, potential_failure_mode, ai_fmea_chunk, 
                                                        expected_failure_modes,  boundary_conditions_list, interaction_type_list, conversation_history)
        improved_line_items_list = FmeaDataHandler.generate_output_with_llm_call(context)
        return improved_line_items_list
    
    def generate_root_causes_based_items(self, query, context_documents,
                                    boundary_conditions_list=None, interaction_type_list=None, potential_failure_mode=None, existing_item_functions=None, root_cause=None, item_fun=None):
        context = self._create_root_cause_based_line_items('generate_root_cause_based_items_prompt', query, context_documents,
                                                        boundary_conditions_list, interaction_type_list, potential_failure_mode, existing_item_functions, root_cause, item_fun)
        root_cause_based_items_list = FmeaDataHandler.generate_output_with_llm_call(context)
        return root_cause_based_items_list

    def generic_response(self, query, conversation_history):     
        lambot_documents = self._retrieve(ToolInput(query=query))
        llm_contexts = [document.llm_context for document in lambot_documents if hasattr(document, StaticFilters.LLMCONTEXT)]
        response = self.answer_generic_questions(llm_contexts, query, conversation_history)
        return response

    def generate_root_cause_based_fmea(self, query, design_requirements=None, filter_keyword=None,
                                        boundary_conditions_list=None, interaction_type_list=None, existing_item_functions=None):
        try:
            item_functions = self.generate_item_functions(design_requirements)
            item_functions = eval(item_functions.content)
            
            potential_failure_modes = self.generate_potential_failure_modes(item_functions)
            potential_failure_modes = eval(potential_failure_modes.content)
            if all(element == "" for element in boundary_conditions_list):
                root_causes_list = [""] * len(potential_failure_modes)
            else:
                predefined_root_causes = StaticData.interaction_type
                root_causes_mapping_list = FmeaDataHandler.map_predefined_root_causes(predefined_root_causes, interaction_type_list)
                
                raw_root_causes = self.add_component_name(design_requirements, boundary_conditions_list, interaction_type_list, root_causes_mapping_list)
                root_causes_list = eval(raw_root_causes.content)
            
            rows = []

            def process_failure(failure_mode, root_cause, item_fun):
                lambot_documents = self._retrieve(ToolInput(query=failure_mode), filter_keyword=filter_keyword)
                llm_contexts = [document.llm_context for document in lambot_documents if hasattr(document, StaticFilters.LLMCONTEXT)]

                missing_line_items_list = self.generate_root_causes_based_items(query,
                    llm_contexts, boundary_conditions_list, interaction_type_list, failure_mode, existing_item_functions, root_cause, item_fun
                )
                missing_line_items = missing_line_items_list.content

                row_data = FmeaDataHandler.parse_missing_line_items(missing_line_items)
                return row_data

            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = [
                    executor.submit(process_failure, failure_mode, root_cause, item_fun)
                    for failure_mode, root_cause, item_fun in zip(
                        potential_failure_modes, root_causes_list, item_functions
                    )
                ]
                
                for future in futures:
                    rows.extend(future.result())

            df = pd.DataFrame(rows)
            current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df["Date"] = current_timestamp
            df["Type"] = "AI Filled"
            return df
        except Exception as e:
            error_message = f"Failed to Generate PDR based FMEA: {str(e)}"
            return {"status": "error", "message": error_message}

    def generate_fmea_template_parallel(self, query, filled_fmea=None, design_requirements=None, filter_keyword=None,
                                        boundary_conditions_list=None, interaction_type_list=None, conversation_history=None, intent_response=None):
        try:
            predefined_root_causes = StaticData.interaction_type
            root_causes_mapping_list = FmeaDataHandler.map_predefined_root_causes(predefined_root_causes, interaction_type_list)
            existing_item_functions = filled_fmea[StaticFilters.ITEMFUNCTION].unique()
            
            item_functions = self.generate_item_functions(design_requirements)
            item_functions = eval(item_functions.content)
            
            expected_failure_modes = self.generate_potential_failure_modes(item_functions)
            expected_failure_modes = eval(expected_failure_modes.content)
            
            unique_failure_modes = list(filled_fmea[StaticFilters.POTENTIALFAILUREMODE].unique())
            
            if len(unique_failure_modes) > 15 and StaticFilters.RPN in filled_fmea.columns:
                filled_fmea = filled_fmea[filled_fmea[StaticFilters.RPN] > 70]
            
            if intent_response == "Add Root Causes":
                unique_failure_modes = expected_failure_modes
            else:
                if 'Type' in filled_fmea.columns:
                    ai_potentil_failure_modes = filled_fmea[StaticFilters.POTENTIALFAILUREMODE].unique()
                    ai_unique_failure_modes = self.filter_potential_failure_modes(ai_potentil_failure_modes, query)
                    unique_failure_modes = eval(ai_unique_failure_modes.content)
                else:    
                    unique_failure_modes = list(filled_fmea[StaticFilters.POTENTIALFAILUREMODE].unique())
            
            rows = []

            def process_failure(unique_failure_mode, root_cause=None):
                mode_chunk_df = filled_fmea[filled_fmea[StaticFilters.POTENTIALFAILUREMODE] == unique_failure_mode]
                fmea_chunk = mode_chunk_df.to_string(index=False)
                
                failure_mode = f'{unique_failure_mode}'
                lambot_documents = self._retrieve(ToolInput(query=failure_mode), filter_keyword=filter_keyword)
                llm_contexts = [document.llm_context for document in lambot_documents if hasattr(document, StaticFilters.LLMCONTEXT)]
                
                if intent_response == "Add Root Causes":
                    fmea_chunk = ''
                    missing_line_items_list = self.generate_missing_line_items(query,
                        llm_contexts, unique_failure_mode, fmea_chunk, expected_failure_modes,
                        boundary_conditions_list, interaction_type_list, conversation_history
                    )
                    missing_line_items = missing_line_items_list.content                
                else:
                    if 'Type' in filled_fmea.columns:
                        improved_line_items_list = self.generate_improved_line_items(query,
                            llm_contexts, unique_failure_mode, fmea_chunk, expected_failure_modes,
                            boundary_conditions_list, interaction_type_list, conversation_history
                        )
                        missing_line_items = improved_line_items_list.content
                    else:
                        missing_line_items_list = self.generate_missing_line_items(query,
                            llm_contexts, unique_failure_mode, fmea_chunk, existing_item_functions,
                            boundary_conditions_list, interaction_type_list, conversation_history,
                            root_cause
                        )
                        missing_line_items = missing_line_items_list.content
                row_data = FmeaDataHandler.parse_missing_line_items(missing_line_items)
                return row_data
            
            num_failure_modes = len(unique_failure_modes)
            if num_failure_modes >= 100:
                workers = math.ceil(num_failure_modes / 10)
            elif num_failure_modes >= 30:
                workers = math.ceil(num_failure_modes / 5)
            else:
                workers = 3   
                    
            with ThreadPoolExecutor(max_workers=workers) as executor:
                if len(unique_failure_modes)>len(root_causes_mapping_list):
                    futures = [
                        executor.submit(process_failure, unique_failure_modes[i], root_causes_mapping_list[i])
                        for i in range(len(root_causes_mapping_list))
                    ]  
                        
                    futures.extend([
                        executor.submit(process_failure, unique_failure_mode)
                        for unique_failure_mode in unique_failure_modes[len(root_causes_mapping_list):]
                    ])
                else:
                    futures = [
                        executor.submit(process_failure, unique_failure_mode)
                        for unique_failure_mode in unique_failure_modes
                    ]
                
                for future in futures:
                    rows.extend(future.result())

            df = pd.DataFrame(rows)
            return df
        except Exception as e:
            error_message = f"Failed to Generate Line Items for FMEA: {str(e)}"
            return {"status": "error", "message": error_message}

    def  process_fmea_results(self, query, filled_fmea=None, design_requirements=None, filter_keyword=None, file_name=None, boundary_conditions_list=None, interaction_type_list=None, conversation_history=None, intent_response=None, original_design_req=None):
        self.dispatch_intermediate_step(intermediate_step=IntermediateStep(message="FMEA generation in progress, please wait and do not refresh the browser as it might take few minutes…"))
        if intent_response == "Add Root Causes":
            df_ai_filled = filled_fmea
        else:
            if "Type" in filled_fmea.columns:
                df_ai_filled = filled_fmea[filled_fmea['Type'] == 'AI Filled']
            else:
                df_ai_filled = filled_fmea

        try:
            fmea_df = self.generate_fmea_template_parallel(query, df_ai_filled, design_requirements, filter_keyword,
                                        boundary_conditions_list, interaction_type_list, conversation_history, intent_response)
        except Exception as e:
            error_message = f"Failed to Initialize FMEA fields from Historical FMEA: {str(e)}"
            return {"status": "error", "message": error_message}
        try:
            fmea_df = fmea_df.sort_values(by='Item Function', ascending=True).reset_index(drop=True)
            clean_df = FmeaDataHandler.combine_filled_and_generated_fmea(filled_fmea, fmea_df)
        except Exception as e:   
            error_message = f"Failed to clean FMEA data: {str(e)}"
            return {"status": "error", "message": error_message}
        try:
            root_cause_df = self.generate_root_cause_based_fmea(query, original_design_req, filter_keyword,
                                        boundary_conditions_list, interaction_type_list)
            root_cause_df = root_cause_df.sort_values(by='Item Function', ascending=True).reset_index(drop=True)
            final_df = pd.concat([clean_df, root_cause_df], ignore_index=True)
            final_df.loc[~((final_df[StaticFilters.CLASS] == "I") | (final_df[StaticFilters.RPN] >= 125)) & (final_df["Type"] != "Manually Filled"), StaticFilters.RECOMMENDEDCORRECTIVEACTION] = ""
        except Exception as e:   
            error_message = f"Failed to generate line items for pre-defined root causes: {str(e)}"
            return {"status": "error", "message": error_message}
        try:
            self.dispatch_intermediate_step(intermediate_step=IntermediateStep(message="FMEA generation completed and its getting dispatched…"))
            blob_url = self.upload_dataframe_to_adls(dataframe=final_df, file_name=file_name)
        except Exception as e:
            error_message = f"Failed to upload FMEA template to ADLS: {str(e)}"
            return {"status": "error", "message": error_message}
        
        fmea_tool_artifact = ToolArtifact(
            content=final_df.iloc[2:10].to_markdown(),
            display_name="FMEA", 
            tool_name="fmea_creation_agent_tool",
            url=blob_url,
            url_display_name="Download FMEA Template"
        )
        
        self.dispatch_tool_artifact(fmea_tool_artifact)
        
        return final_df
    
    def _run(self, query: ToolInput) -> str:   
        """Run the retriever tool synchronously."""
        messages = asyncio.run(self.get_conversation_history())
        conversation_history = messages[-11:-1]

        intent_detection_prompt = (
            f"{StaticData.INTENT_DETECTION_PROMPT}\n{query}\n{self.file_attachments}\n"
        )
        intent_response = FmeaDataHandler.generate_output_with_llm_call(intent_detection_prompt).content
        
        if intent_response == "Generic Question":
            try:                
                self.dispatch_intermediate_step(
                    intermediate_step=IntermediateStep(message="Processing your query and getting context from FMEA Datasource, please wait…")
                )
                response = self.generic_response(query, conversation_history)
                return response
            except Exception as e:
                error_message = f"Unable to generate generic response: {str(e)}"
                return {"status": "error", "message": error_message}

        elif intent_response == "File Summarization":
            try:
                if not self.file_attachments:
                    return {"status": "error", "message": "File Summarization requires at least one uploaded file."}

                for file in self.file_attachments:
                    if file.mime == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                        self.dispatch_intermediate_step(intermediate_step=IntermediateStep(message="Extracting content from Filled FMEA Excel file…"))
                        fmea_df = FmeaDataHandler.extract_fields_from_filled_fmea(base64.b64decode(file.value))
                        unique_failure_modes = list(fmea_df[StaticFilters.POTENTIALFAILUREMODE].unique())
                        if len(unique_failure_modes) > 50 and StaticFilters.RPN in fmea_df.columns:
                            final_df = fmea_df[fmea_df[StaticFilters.RPN] >= 70]
                            file_content = final_df.to_markdown(index=False)
                        else:
                            file_content = fmea_df.to_markdown(index=False)
                    elif file.mime == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
                        self.dispatch_intermediate_step(intermediate_step=IntermediateStep(message="Extracting content from Design Requirement PDR Slide…"))
                        file_content = FmeaDataHandler.extract_pdr_slide_content(base64.b64decode(file.value))
                    else:
                        self.dispatch_intermediate_step(intermediate_step=IntermediateStep(message="Extracting content from uploaded file…"))
                        file_content = BytesIO(base64.b64decode(file.value))
                
                self.dispatch_intermediate_step(intermediate_step=IntermediateStep(message="Summarizing the content of the uploaded file…"))
                file_summary_prompt = (f"{StaticData.FILE_SUMMARIZATION_PROMPT}\n{query}\n{file_content}\n")
                summary = FmeaDataHandler.generate_output_with_llm_call(file_summary_prompt)
                return summary
            except Exception as e:
               error_message = f"Unable to generate summary for uploaded file: {str(e)}"
               return {"status": "error", "message": error_message}

        elif intent_response == "FMEA Creation":
            try:
                if not self.file_attachments:
                    error_message = "Updating FMEA requires both a Draft FMEA Excel file and a PDR PowerPoint file."
                    return {"status": "error", "message": error_message}
                
                self.dispatch_intermediate_step(intermediate_step=IntermediateStep(message="Analyzing uploaded files for FMEA creation…"))

                filled_fmea_bytes = None
                pptx_bytes = None
                
                for file in self.file_attachments:
                    if file.mime == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                        filled_fmea_bytes = file.value
                    elif file.mime == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
                        pptx_bytes = file.value

                if not filled_fmea_bytes:
                    error_message = "FMEA Creation requires a Draft FMEA Excel file."
                    return {"status": "error", "message": error_message}
                    
                if not pptx_bytes:
                    error_message = "FMEA Creation requires a PDR PowerPoint file."
                    return {"status": "error", "message": error_message}
                
                self.dispatch_intermediate_step(intermediate_step=IntermediateStep(message="Extracting content from Draft FMEA Spreadsheet…"))
                filled_fmea = FmeaDataHandler.extract_fields_from_filled_fmea(base64.b64decode(filled_fmea_bytes))

                self.dispatch_intermediate_step(intermediate_step=IntermediateStep(message="Extracting content from design requirement…"))
                filter_keyword, part_value, pg_name, bu_name, tool, original_design_req, boundary_conditions_list, interaction_type_list = FmeaDataHandler.create_design_requirements_from_pptx_bytes(base64.b64decode(pptx_bytes))
                
                common_item_functions = StaticData.common_item_functions
                design_req_with_common = original_design_req + common_item_functions

                file_name = f"{pg_name}_{bu_name}_FMEA_of_{tool}_{filter_keyword}_{part_value}_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"

                final_df = self.process_fmea_results(
                    query, filled_fmea, design_req_with_common, filter_keyword, file_name, boundary_conditions_list, interaction_type_list, conversation_history, intent_response, original_design_req
                )
                self.dispatch_intermediate_step(
                    intermediate_step=IntermediateStep(message="FMEA Creation Completed…")
                )
                
                self.dispatch_intermediate_step(intermediate_step=IntermediateStep(message="Generating FMEA summary, please wait..."))
                unique_failure_modes = list(final_df[StaticFilters.POTENTIALFAILUREMODE].unique())
                if len(unique_failure_modes) > 50 and StaticFilters.RPN in final_df.columns:
                    final_fmea_df = final_df[final_df[StaticFilters.RPN] > 70]
                else:
                    final_fmea_df = final_df
                fmea_content = final_fmea_df.to_markdown(index=False)
                fmea_summary_prompt = (f"{StaticData.FMEA_SUMMARIZATION_PROMPT}\n{fmea_content}\n")
                fmea_summary_raw = FmeaDataHandler.generate_output_with_llm_call(fmea_summary_prompt)
                fmea_summary = fmea_summary_raw.content 
                
                tool_output = fmea_summary
                return tool_output
            except Exception as e:
               error_message = f"Unable to generate FMEA: {str(e)}"
               return {"status": "error", "message": error_message}
            
        else:
            response = self.generic_response(query, conversation_history)
            return response