import json
from src.models import LamBotChatResponse
from src.core.bots.lambot import LamBot
from src.core.utils import convert_lambot_documents_to_citations
from src.core.chat.utils import extract_and_renumber_citations, extract_indexes_queried_by_agent
from src.models.logging import TokenUsageDetails, ResponseInfo
from src.core.bots.followup_questions_generator_bot import FollowUpQuestionGeneratorBot
from src.core.utils.log_trace import log_trace_event
from langchain_core.messages import AIMessageChunk, AIMessage
from src.models.constants import IntakeItem
from dotenv import load_dotenv

load_dotenv(override=True)

from typing import List, Dict, Any, Union, AsyncGenerator

class ConversationEngine:
    def __init__(self, bot: LamBot):
        """
        Initialize the ConversationEngine with the given bot.

        Args:
            bot (LamBot): The bot instance to use for handling conversations.
        """
        self._bot = bot
        self._callback_handler = bot.langfuse_manager.callback_handler
        self.is_enterprise_lambot = self._bot.bot_config.display_name == "Enterprise LamBot"
        self._accumulated_input_tokens = 0
        self._accumulated_output_tokens = 0

    async def _supply_intake_items_to_tools(self, messages):
        """
        Supplies all relevant intake items (e.g., conversation history, file attachments) 
        to the tools that support them, based on the bot's intake flags.

        This ensures that tools have the necessary context and resources to perform their tasks.
        """
        if self._bot.intake_flags:
            for tool in self._bot._tools:
                if tool.allowed_intakes:
                    # Check and supply conversation history if allowed
                    if IntakeItem.CONVERSATION_HISTORY in self._bot.intake_flags and IntakeItem.CONVERSATION_HISTORY in tool.allowed_intakes:
                        await tool.set_conversation_history(messages)

                    # Check and supply file attachments if allowed
                    if IntakeItem.FILE_ATTACHMENTS in self._bot.intake_flags and IntakeItem.FILE_ATTACHMENTS in tool.allowed_intakes:
                        await tool.set_file_attachments(self._bot.file_attachments)

    async def _generate_streaming_response(self, messages: List[Dict[str, Any]], trace_id: str):
        """
        Handle a conversation based on the messages.

        Args:
            messages (List[Dict[str, Any]]): The list of messages to use in the conversation.
            trace_id (str): The trace ID for E2E tracing.
        """
        first_token_streamed = False

        # Update the chat history in the bot
        self._bot.chat_history = messages[:-1]
        self._bot._configure_agent()
        user_question = messages[-1]["content"]

        self._bot.metric_api_client.make_async_log_trace_request(
            log_message=f"LamBotId: {self._bot.bot_config.id} "
                        f"Messaging: {user_question if not self.is_enterprise_lambot else ''} "
                        f"with correlationID: {self._bot.metric_api_client.correlation_id}",
            log_level="Information",
        )

        await self._supply_intake_items_to_tools(messages)

        agent_executor = self._bot.agent_executor
        agent_executor_input, invoke_config = self._bot._prepare_agent_execution(messages)
            
        lambot_documents = all_citations = followup_question_token_usage = followup_questions = None
        agent_executor_output = []
        current_chunk = "" # Current chunk, resetting each time text streams unless ending with a possible partial citation
        citation_map = {} # Maps citation string (e.g. "[3]") with citation counter (e.g. 1). IMPORTANT for LAMBOT-13 - Explainability drawer

        llm_response = ""
        async for event in agent_executor.astream_events(
            agent_executor_input,
            version="v2",
            config=invoke_config,
        ):
            kind = event["event"]
            # self._bot.logger.debug(f"Event kind: {kind} Event name: {event['name']}")
            if (kind == "on_chat_model_stream") and ('lambot-agent-llm' in event.get("tags", []) or 'supervisor' in event.get("tags", [])):

                content = event["data"]["chunk"].content
                if not content: continue
                if not first_token_streamed:
                    first_token_streamed = True
                    log_trace_event(
                        trace_id=trace_id,
                        step="first_token_streamed",
                    )
                current_chunk += content
                # Extract and renumber citations
                chunk_to_yield, current_chunk, citations_to_yield = extract_and_renumber_citations(current_chunk, citation_map, all_citations)

                # Yield any citations, then yield the chunk
                if citations_to_yield:
                    yield LamBotChatResponse(chunk="", citations=citations_to_yield).model_dump_json() + "\n"
                yield LamBotChatResponse(chunk=chunk_to_yield, citations=[]).model_dump_json() + "\n"

            elif kind == "on_custom_event" and event["name"] == "tool_artifact":
                artifact = event["data"]["artifact"]
                yield LamBotChatResponse(
                        chunk="", citations=[], tool_artifacts=[artifact]
                ).model_dump_json() + "\n"

            elif kind == "on_custom_event" and event["name"] == "intermediate_step":
                intermediate_step = event["data"]["intermediate"]
                yield LamBotChatResponse(
                    chunk="", citations=[], intermediate_steps=[intermediate_step]
                ).model_dump_json() + "\n"

            # Store documents from the last on_retriever_end event
            elif kind == "on_retriever_end":
                lambot_documents = event["data"].get("output")
                all_citations = convert_lambot_documents_to_citations(lambot_documents, include_metadata=True)
            
            elif kind == "on_chat_model_end":
                output = event["data"]["output"]
                if isinstance(output, AIMessageChunk):
                    usage = output.usage_metadata
                    if usage:
                        self._accumulated_input_tokens += usage.get("input_tokens", 0)
                        self._accumulated_output_tokens += usage.get("output_tokens", 0)                    

            # Collect the final agent output for suggested follow up questions
            elif kind == "on_chain_end" and (event["name"] == "AgentExecutor"):
                agent_executor_output = event["data"]["output"]["messages"]
                for message in agent_executor_output:
                    if isinstance(message, AIMessage):
                        llm_response = (
                            message.content
                        )

            else:
                yield LamBotChatResponse(
                    chunk="", citations=[]
                ).model_dump_json() + "\n"

        # Rare edge case: Response ends with partial citation.
        if current_chunk:
            yield LamBotChatResponse(
                chunk=current_chunk,
                citations=[],
            ).model_dump_json() + "\n"

        # After processing all events, yield the documents from the last on_retriever_end event
        # Explanation:
        # In a multi-retriever setup, each retriever returns documents, triggering an "on_retriever_end" event.
        # We're only interested in the final pooled documents after all retrievals and reranking and filtering to top_k.
        # By yielding only the last set, we ensure the most relevant documents are provided.
        # TBD: Replace this with a more robust solution that explicitly handles which retrievers to yield from.
        if all_citations:
            # Only yield unused citations here
            unused_citations = [citation for citation in all_citations if not citation.is_used]

            yield LamBotChatResponse(
                chunk="",
                citations=unused_citations,
            ).model_dump_json() + "\n"


        if self._bot.bot_config.suggest_followup_questions:
            followup_question_bot = FollowUpQuestionGeneratorBot(
                lambot_display_name=self._bot.bot_config.display_name,
                langfuse_manager=self._bot.langfuse_manager
            )
            followup_questions = followup_question_bot.generate_followup_questions(messages, agent_executor_output)

            log_trace_event(
                trace_id=trace_id,
                step="followup_questions_created",
            )

            yield LamBotChatResponse(
                chunk="",
                citations=[],
                followup_questions=followup_questions,
            ).model_dump_json() + "\n"
            followup_question_token_usage = followup_question_bot.usage_metadata


        # Calculate total token usage details
        total_token_usage_details = TokenUsageDetails(
            prompt_tokens=self._accumulated_input_tokens
            + (
                followup_question_token_usage.prompt_tokens
                if followup_question_token_usage
                else 0
            ),
            completion_tokens=self._accumulated_output_tokens
            + (
                followup_question_token_usage.completion_tokens
                if followup_question_token_usage
                else 0
            ),
            total_tokens_used=self._accumulated_input_tokens
            + self._accumulated_output_tokens
            + (
                followup_question_token_usage.total_tokens_used
                if followup_question_token_usage
                else 0
            ),
        )

        response_info = ResponseInfo(
            user_email=self._bot.metric_api_client.user_email,
            prompt=user_question if not self.is_enterprise_lambot else '',
            response=llm_response if not self.is_enterprise_lambot else '',
            gpt_model=self._bot._query_config.language_model.name,
            temperature=self._bot._query_config.temperature,
            indexes_used=extract_indexes_queried_by_agent(self._bot),
            selected_data_sources = [
                tool_config.display_name
                for tool_config in self._bot._query_config.selected_tools
            ] if not self.is_enterprise_lambot else [],
            follow_up_questions=followup_questions or [],
            LamBotId=self._bot.bot_config.id,
            LamBotName=self._bot.bot_config.display_name,
            token_consumption_details=total_token_usage_details,
        )

        self._bot.metric_api_client.make_async_log_trace_request(
            log_message=f"Response info: {response_info.model_dump_json()} with correlationID: {self._bot.metric_api_client.correlation_id}",
            log_level="Information",
        )

        yield LamBotChatResponse(
            chunk="",
            citations=[],
            done=True,
        ).model_dump_json() + "\n"

        log_trace_event(
            trace_id=trace_id,
            step="full_response_serviced",
        )

    async def _generate_aggregated_response(self, messages: List[Dict[str, Any]], trace_id: str) -> LamBotChatResponse:
        """
        Calls generate_streaming_response and aggregates all the streamed LamBotChatResponse messages into one final response.

        Args:
            messages: A list of messages to feed into the conversation.
            trace_id (str): The trace ID for logging/tracing purposes.

        Returns:
            LamBotChatResponse: A final response that aggregates chunks, citations, followup questions,
                                tool artifacts, and intermediate steps.
        """
        accumulated_chunk = ""
        accumulated_citations = []
        accumulated_followup_questions = []
        accumulated_tool_artifacts = []
        accumulated_intermediate_steps = []

        async for response_json in self._generate_streaming_response(messages, trace_id):
            # Parse each JSON response back into a LamBotChatResponse object.
            response_dict = json.loads(response_json)
            response_obj = LamBotChatResponse(**response_dict)

            # Concatenate the chunk text.
            accumulated_chunk += response_obj.chunk

            # Extend citations.
            if response_obj.citations:
                accumulated_citations.extend(response_obj.citations)

            # Extend followup questions.
            if response_obj.followup_questions:
                accumulated_followup_questions.extend(response_obj.followup_questions)

            # Extend tool artifacts.
            if response_obj.tool_artifacts:
                accumulated_tool_artifacts.extend(response_obj.tool_artifacts)

            # Extend intermediate steps.
            if response_obj.intermediate_steps:
                accumulated_intermediate_steps.extend(response_obj.intermediate_steps)

            # Stop processing once the done flag is encountered.
            if response_obj.done:
                break

        final_response = LamBotChatResponse(
            chunk=accumulated_chunk,
            citations=accumulated_citations,
            followup_questions=accumulated_followup_questions if accumulated_followup_questions else None,
            tool_artifacts=accumulated_tool_artifacts if accumulated_tool_artifacts else None,
            intermediate_steps=accumulated_intermediate_steps if accumulated_intermediate_steps else None,
            done=True
        )
        return final_response
    
    async def generate_response(self, messages: List[Dict[str, Any]], trace_id: str, streaming: bool = False) -> Union[LamBotChatResponse, AsyncGenerator[str, None]]:
        """
        Public method to generate response using either streaming or aggregated method based on the streaming flag.
        
        Args:
            messages: A list of conversation messages.
            trace_id (str): Trace id for logging/tracing purposes.
            streaming (bool): If True, stream the response; if False, return an aggregated response.
        
        Returns:
            Either an async generator yielding streaming responses or a single aggregated LamBotChatResponse.
        """
        if streaming:
            # Delegate to the streaming function.
            async for streamed_response in self._generate_streaming_response(messages, trace_id):
                yield streamed_response
        else:
            # Return the fully aggregated response.
            aggregated_response = await self._generate_aggregated_response(messages, trace_id)
            yield aggregated_response