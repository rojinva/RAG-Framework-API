import base64

from PIL import Image
from io import BytesIO
from typing import List

from openai.types.beta.threads.runs.run_step import RunStep
from openai.types.beta.threads.runs.tool_calls_step_details import ToolCallsStepDetails
from openai.types.beta.threads.runs.code_interpreter_tool_call import (
    CodeInterpreterToolCall,
)
from openai.types.beta.threads.runs.message_creation_step_details import (
    MessageCreationStepDetails,
)
from openai.types.beta.threads.message import Message

from src.models.tool import ToolArtifact
from src.models.intermediate_step import IntermediateStep
from src.core.base import LamBotEvents
from src.models.constants import MimeType
from src.core.tools.community.code_interpreter_tool.file_manager import (
    AssistantFileManager,
)
from src.core.base.utils import upload_data_to_adls

class RunStepProcessor(LamBotEvents):
    def __init__(self, client, thread_id: str, run_id: str):
        self.client = client
        self.thread_id = thread_id
        self.run_id = run_id
        self.file_manager = AssistantFileManager()
        self.name = "code_interpreter"
        self.dispatched_events = set()  # Set to track dispatched artifact contents

    @staticmethod
    def resize_image(image_bytes, max_width=800):
        """
        Resize the image to the specified width while maintaining aspect ratio.
        """
        image = Image.open(BytesIO(image_bytes))
        aspect_ratio = image.height / image.width
        new_height = int(max_width * aspect_ratio)
        resized_image = image.resize((max_width, new_height))

        buffer = BytesIO()
        resized_image.save(buffer, format="PNG")
        return buffer.getvalue()

    def dispatch_code(self, tool_call: CodeInterpreterToolCall):
        """
        Extracts the code input from a CodeInterpreterToolCall object.
        """
        code_tool_artifact = ToolArtifact(
            content=f"```\n{tool_call.code_interpreter.input}\n```",
            display_name="Source code",
            tool_name=self.name,
            content_type=MimeType.MARKDOWN,
        )
        if code_tool_artifact not in self.dispatched_events:
            self.dispatched_events.add(code_tool_artifact)
            self.dispatch_tool_artifact(code_tool_artifact)

    def dispatch_message_content(self, message_creation: MessageCreationStepDetails):
        """
        Extracts the text content from a MessageCreationStepDetails object.
        """
        message_id = message_creation.message_creation.message_id
        message: Message = self.client.beta.threads.messages.retrieve(
            message_id=message_id, thread_id=self.thread_id
        )
        # Extract the text content from the message
        text_content = ""
        for content_block in message.content:
            if content_block.type == "text":
                text_content += content_block.text.value + "\n"

        # Strip the text content to remove leading/trailing whitespace
        stripped_text_content = text_content.strip()

        # Skip processing if the stripped text content is empty
        if not stripped_text_content:
            return

        intermediate_step = IntermediateStep(message=stripped_text_content)
        if intermediate_step not in self.dispatched_events:
            self.dispatched_events.add(intermediate_step)
            self.dispatch_intermediate_step(intermediate_step)

    def _fetch_run_steps(self) -> List[RunStep]:
        """
        Fetches the run steps from the client using the thread_id and run_id.

        Returns:
            List[RunStep]: A list of RunStep objects.
        """
        run_steps = self.client.beta.threads.runs.steps.list(
            thread_id=self.thread_id, run_id=self.run_id
        )
        return run_steps

    def process_run_steps(self):
        """
        Processes the run steps to extract code inputs and file IDs.
        """
        run_steps = self._fetch_run_steps()
        for step in run_steps:
            if (
                isinstance(step.step_details, ToolCallsStepDetails)
                and step.step_details.tool_calls
            ):
                for tool_call in step.step_details.tool_calls:
                    if isinstance(tool_call, CodeInterpreterToolCall):
                        self.dispatch_code(tool_call)
            elif isinstance(step.step_details, MessageCreationStepDetails):
                self.dispatch_message_content(step.step_details)

    async def dispatch_files_generated_by_assistant(self):
        files = await self.file_manager.get_files_from_thread(self.thread_id)
        for file in files:
            if file.file_name.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
                resized_image_bytes = self.resize_image(file.file_bytes)
                base64_image = base64.b64encode(resized_image_bytes).decode("utf-8")
                markdown_image = f"![image](data:image/png;base64,{base64_image})"
                image_tool_artifact = ToolArtifact(
                    content=markdown_image,
                    display_name="Output image",
                    tool_name=self.name,
                    content_type=MimeType.PNG,
                )
                self.dispatch_tool_artifact(image_tool_artifact)
            else:
                signed_url = upload_data_to_adls(
                    tool_name=self.name, file_bytes=file.file_bytes, file_name=file.file_name
                )
                file_tool_artifact = ToolArtifact(
                    content="",
                    display_name="Generated file",
                    tool_name=self.name,
                    url=signed_url,
                    url_display_name=file.file_name,
                )
                self.dispatch_tool_artifact(file_tool_artifact)

    def clear_dispatched_events(self):
        """
        Clears the set of dispatched artifacts.
        """
        self.dispatched_events.clear()
        print("Dispatched events have been cleared.")
