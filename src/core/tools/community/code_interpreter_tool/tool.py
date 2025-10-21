import os
import logging
import asyncio
from pydantic import BaseModel, Field
from typing import List, Optional, Type, Annotated, Any

from openai import AzureOpenAI
from openai.types.beta.threads.message import Message

from src.core.base import LamBotTool
from src.models import ToolType
from src.core.tools.community.code_interpreter_tool.lambot_openai_assistant_runnable import (
    LamBotOpenAIAssistantRunnable,
)
from src.core.tools.community.code_interpreter_tool.utils import (
    split_messages_into_history_and_last_user_query,
)
from src.core.tools.community.code_interpreter_tool.prompts import (
    CODE_INTERPRETER_ASSISTANT_SYSTEM_MESSAGE,
    CODE_INTERPRETER_TOOL_DESCRIPTION_PROMPT,
    CODE_INTERPRETER_TOOL_INSTRUCTION_PROMPT,
)
from src.core.tools.community.code_interpreter_tool.file_manager import (
    AssistantFileManager,
)
from langchain_core.tools import InjectedToolArg
from src.models.constants import IntakeItem
from src.models.intermediate_step import IntermediateStep
from src.clients import LifespanClients

from dotenv import load_dotenv

load_dotenv(override=True)


# --------------------------------------------------------------------------- #
# Pydantic schema
# --------------------------------------------------------------------------- #
class CodeInterpreterArgsSchema(BaseModel):
    """
    Input schema for the Code-Interpreter tool.
    conversation_history will generally be injected by the orchestration layer,
    but we allow the caller to provide (or omit) it.
    """

    messages: Optional[Annotated[List[dict], InjectedToolArg]] = Field(
        None, description="List of messages in {role, content} format."
    )
    file_attachments: Optional[Annotated[Any, InjectedToolArg]] = Field(
        None, description="List of file attachments to be processed by the tool."
    )


class CodeInterpreterTool(LamBotTool):
    args_schema: Type[BaseModel] = CodeInterpreterArgsSchema
    assistant: LamBotOpenAIAssistantRunnable = Field(
        default=None, description="OpenAI Assistant V2 instance for code interpretation."
    )
    client: AzureOpenAI = Field(
        default=LifespanClients.get_instance().azure_openai.azure_use2_region_client,
        description="Azure OpenAI client instance.",
    )
    file_manager: AssistantFileManager = Field(
        default=None,
        description="File manager for handling file uploads and attachments.",
    )

    def __init__(self):
        super().__init__(
            name="code_interpreter",
            description=self._get_prompt(
                prompt_name="CODE_INTERPRETER_TOOL_DESCRIPTION_PROMPT",
                fallback_prompt=CODE_INTERPRETER_TOOL_DESCRIPTION_PROMPT,
                label=os.getenv("LANGFUSE_LABEL", "dev"),
            ),
            tool_type=ToolType.non_retriever_tool,
            allowed_intakes=[
                IntakeItem.CONVERSATION_HISTORY,
                IntakeItem.FILE_ATTACHMENTS,
            ],
        )
        self.assistant = None
        self.file_manager = AssistantFileManager()

    async def _create_assistant(self):
        """
        Create the assistant instance if it hasn't been created yet.
        This is useful for async initialization.
        """
        if not self.assistant:
            self.assistant = await LamBotOpenAIAssistantRunnable.acreate_assistant(
                name="LamBot Code Interpreter Assistant",
                instructions=self._get_prompt(
                    prompt_name="CODE_INTERPRETER_ASSISTANT_SYSTEM_MESSAGE",
                    fallback_prompt=CODE_INTERPRETER_ASSISTANT_SYSTEM_MESSAGE,
                    label=os.getenv("LANGFUSE_LABEL", "dev"),
                ),
                tools=[{"type": "code_interpreter"}],
                model="gpt-4o-gs",
                async_client=LifespanClients.get_instance().azure_openai.async_azure_use2_region_client,
                client=LifespanClients.get_instance().azure_openai.azure_use2_region_client,
                temperature=0.0,
            )

    async def _execute(self, **kwargs) -> str:
        """
        Shared logic for both sync and async calls.
        """

        if not self.assistant:
            await self._create_assistant()

        messages = await self.get_conversation_history()
        file_attachments = await self.get_file_attachments()

        self.dispatch_intermediate_step(
            intermediate_step=IntermediateStep(
                message="Getting the code interpreter tool ready..."
            )
        )
        conversation_history, query = split_messages_into_history_and_last_user_query(
            messages=messages
        )

        file_mappings = None

        try:
            if file_attachments:
                # Upload files from message attachments
                file_mappings = await self.file_manager.upload_files_to_assistant(
                    file_attachments
                )
                if file_mappings:
                    self.dispatch_intermediate_step(
                        intermediate_step=IntermediateStep(
                            message=f"Uploaded {len(file_mappings)} file(s) for analysis"
                        )
                    )
                else:
                    self.dispatch_intermediate_step(
                        intermediate_step=IntermediateStep(
                            message="No files were successfully uploaded"
                        )
                    )

        except Exception as e:
            logging.error(f"Error uploading files: {str(e)}")
            self.dispatch_intermediate_step(
                intermediate_step=IntermediateStep(
                    message="Error uploading files, proceeding without attachments"
                )
            )

        # Create thread with or without attachments
        thread_id = self.assistant.create_thread(
            conversation_history=conversation_history,
            file_mappings=file_mappings,
        )

        try:
            self.dispatch_intermediate_step(
                intermediate_step=IntermediateStep(
                    message="Running the code interpreter tool..."
                )
            )
            _response = await self.assistant.ainvoke(
                {
                    "content": query,
                    "thread_id": thread_id,
                }
            )
            self.dispatch_intermediate_step(
                intermediate_step=IntermediateStep(
                    message="Processing the response from the code interpreter tool..."
                )
            )
            assistant_response_message: Message = _response[-1]

            _tool_response = ""
            for content in assistant_response_message.content:
                if content.type == "text":
                    _tool_response += content.text.value

            instruction_prompt = self._get_prompt(
                prompt_name="CODE_INTERPRETER_TOOL_INSTRUCTION_PROMPT",
                fallback_prompt=CODE_INTERPRETER_TOOL_INSTRUCTION_PROMPT,
                label=os.getenv("LANGFUSE_LABEL", "dev"),
            )

            tool_response = instruction_prompt + _tool_response
        except Exception as e:
            raise RuntimeError(
                f"An error occurred while running the code interpreter tool: {str(e)}"
            )
        finally:
            # Clean up thread and uploaded files
            self.assistant.delete_thread(thread_id=thread_id)
            if file_mappings:
                await self.file_manager.delete_files(file_mappings=file_mappings)

        return tool_response

    def _run(self, **kwargs) -> str:
        return asyncio.run(self._execute(**kwargs))

    async def _arun(self, **kwargs) -> str:
        return await self._execute(**kwargs)
