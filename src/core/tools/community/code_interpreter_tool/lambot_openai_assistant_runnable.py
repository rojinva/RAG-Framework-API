import asyncio
from time import sleep
from langchain_community.agents.openai_assistant import OpenAIAssistantV2Runnable
from openai.types.beta.threads.run import Run
from openai.types.beta.threads.message_create_params import Attachment

from src.core.tools.community.code_interpreter_tool.run_steps_processor import (
    RunStepProcessor,
)


class LamBotOpenAIAssistantRunnable(OpenAIAssistantV2Runnable):
    async def _await_for_run(self, run_id: str, thread_id: str) -> Run:
        """Wait for the completion of a run. This is an overridden method to handle asynchronous waiting of runs.

        Args:
            run_id (str): The ID of the run to wait for.
            thread_id (str): The ID of the thread associated with the run.

        Returns:
            Run: The result of the run once it is completed.
        """
        in_progress = True
        processor = RunStepProcessor(
            client=self.client, thread_id=thread_id, run_id=run_id
        )
        while in_progress:
            run = await self.async_client.beta.threads.runs.retrieve(
                run_id, thread_id=thread_id
            )
            processor.process_run_steps()
            in_progress = run.status in ("in_progress", "queued")
            if in_progress:
                await asyncio.sleep(self.check_every_ms / 1000)

        await processor.dispatch_files_generated_by_assistant()
        processor.clear_dispatched_events()
        return run

    def _wait_for_run(self, run_id: str, thread_id: str) -> Run:
        """Wait for the completion of a run. This is a synchronous method to handle waiting for runs.

        Args:
            run_id (str): The ID of the run to wait for.
            thread_id (str): The ID of the thread associated with the run.

        Returns:
            Run: The result of the run once it is completed.
        """
        in_progress = True
        processor = RunStepProcessor(
            client=self.client, thread_id=thread_id, run_id=run_id
        )
        while in_progress:
            run = self.client.beta.threads.runs.retrieve(run_id, thread_id=thread_id)
            processor.process_run_steps()
            in_progress = run.status in ("in_progress", "queued")
            if in_progress:
                sleep(self.check_every_ms / 1000)

        processor.dispatch_files_generated_by_assistant()
        processor.clear_dispatched_events()
        return run

    def create_thread(self, conversation_history, file_mappings=None):
        thread = self.client.beta.threads.create()
        attachment_message = None

        if file_mappings:
            attachments = []

            # Prepare the file mapping prompt
            # Link to discussion:
            # https://community.openai.com/t/filenames-in-code-interpreters-assistant-api/989609
            file_mapping_prompt = "\n".join(
                [
                    f"{file_name}: {file_id}"
                    for file_name, file_id in file_mappings.items()
                ]
            )

            file_mapping_llm_content = (
                "The following files are associated with this thread (file names followed by their file id):\n\n"
                f"{file_mapping_prompt}\n\n"
                "These files are now part of the thread and can be used for further processing."
            )

            for _, file_id in file_mappings.items():
                attachments.append(
                    Attachment(file_id=file_id, tools=[{"type": "code_interpreter"}])
                )

            attachment_message = {
                "role": "user",
                "content": file_mapping_llm_content,
                "attachments": attachments,
            }

        if attachment_message:
            # If there is an attachment message, insert it in the second-to-last position
            conversation_history.insert(-1, attachment_message)
        for message in conversation_history:
            message_data = {
                "thread_id": thread.id,
                "role": message["role"],
                "content": message["content"]
            }

            if "attachments" in message:
                message_data["attachments"] = message["attachments"]

            self.client.beta.threads.messages.create(**message_data)

        return thread.id

    def delete_thread(self, thread_id: str):
        """Delete a thread. This is a new method to handle thread deletion.

        Args:
            thread_id (str): The ID of the thread to delete.

        Raises:
            ValueError: If the thread cannot be deleted.
        """
        try:
            self.client.beta.threads.delete(thread_id=thread_id)
            print(f"{thread_id} successfully deleted.")
        except Exception as e:
            raise ValueError(f"Failed to delete thread {thread_id}. Error: {e}")
