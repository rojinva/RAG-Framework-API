import os
import sys
# Adjust the path to include the parent directory
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "src"))
import pytest
import asyncio
from uuid import uuid4
from unittest.mock import patch
from fastapi import HTTPException

pytest_plugins = ('pytest_asyncio',)



class TestChatCompletionService:
        
    @pytest.fixture
    def mock_inits_and_import_chat_completion(self, mocker):
        mock_core_bots = mocker.MagicMock()
        mock_core_bots.LamBot = mocker.MagicMock()
        mock_core_bots.ExceptionAssistBot = mocker.MagicMock()
        mock_log_trace = mocker.MagicMock()
        mock_log_trace.log_trace_event = mocker.MagicMock()
        mock_chat = mocker.MagicMock()
        mock_chat.ConversationEngine = mocker.MagicMock()
        with patch.dict('sys.modules', {
            'src.core.bots': mock_core_bots,
            'src.core.utils.log_trace': mock_log_trace,
            'dotenv.load_dotenv': mocker.MagicMock(),
            'src.core.chat':mock_chat,
            'dotenv': mocker.MagicMock(),
            "langchain_openai": mocker.MagicMock(),
            "src.core.retrievers": mocker.MagicMock(),
            "src.core.retrievers.multi_retriever": mocker.MagicMock(),
            "src.core.retrievers.retriever": mocker.MagicMock(),
        }):
            from src.services.chat_completion.internal import chat_completion
            from src.models import LamBotChatRequest, LamBotConfig, QueryConfig
            from src.models.config import LanguageModelConfig
            from src.models.access_conditions import AccessConditions
            yield chat_completion, mock_core_bots, mock_chat, LamBotChatRequest, QueryConfig, LanguageModelConfig, LamBotConfig, AccessConditions

    @pytest.fixture
    def request_fixture(self, mock_inits_and_import_chat_completion):
        _, _, _, LamBotConfig, _, _, _, _ = mock_inits_and_import_chat_completion #NOSONAR
        return LamBotConfig(
            lambot_id="test_bot",
            messages=[{"role": "user", "content": "Hello"}],
            query_config=None
            )

    @pytest.fixture
    def config_fixture(self, mock_inits_and_import_chat_completion):
        _, _, _, _, QueryConfig, LanguageModelConfig, LamBotConfig, AccessConditions = mock_inits_and_import_chat_completion #NOSONAR
        q_config = QueryConfig(
            system_message="You are a helpful assistant.",
            temperature=0.7,
            selected_tools=[],
            language_model=LanguageModelConfig(
                name="gpt-4o-mini-not-real",
                display_name="GPT-4o Mini",
                description="A smaller version of GPT-4 optimized for speed and efficiency.",
                unsupported_features=[]
            ),
            top_k=5,
            force_tool_call=False
            )
        return LamBotConfig(
            id=uuid4(),
            display_name="Test Bot",
            description="A test bot",
            creator="test_creator",
            api_version="1.0",
            defaultQueryConfig=q_config,
            tools=[],
            agent="tool_calling",
            conversation_starters=[],
            combine_retriever_tools=False,
            suggest_followup_questions=False,
            supported_language_models=[],
            access_conditions=AccessConditions(
                min_tools=0,
                required_tools=[],
                additional_required_security_groups=[])
            )

    async def setup_mock_stream(self, mock_engine, responses, error=None, error_on_item="response2"):
        async def mock_stream_response(*args, **kwargs):
            for item in responses:
                if error and item == error_on_item:
                    raise error("Simulated error for testing")
                yield item
        mock_engine.stream_response = mock_stream_response
        return mock_engine

    @pytest.mark.asyncio
    async def test_chat_completion(self, mock_inits_and_import_chat_completion, request_fixture, config_fixture, mocker):
        chat_completion, _, mock_chat, *_ = mock_inits_and_import_chat_completion #NOSONAR
        
        mock_response_data = ["response1", "response2"]
        mock_engine = mocker.MagicMock()
        mock_engine = await self.setup_mock_stream(mock_engine, mock_response_data)
        mock_chat.ConversationEngine.return_value = mock_engine

        responses = []
        async for resp in chat_completion(request_fixture, config_fixture, trace_id="test_trace_id"):
            responses.append(resp)
        assert responses == mock_response_data

    @pytest.mark.asyncio
    async def test_chat_completion_raise_value_error_capture_http_exception(
        self, mock_inits_and_import_chat_completion, request_fixture, config_fixture, mocker
    ):
        chat_completion, _, mock_chat, *_ = mock_inits_and_import_chat_completion
        
        mock_response_data = ["response1", "response2"]
        mock_engine = mocker.MagicMock()
        mock_engine = await self.setup_mock_stream(mock_engine, mock_response_data, ValueError)
        mock_chat.ConversationEngine.return_value = mock_engine

        responses = []
        with pytest.raises(HTTPException):
            async for resp in chat_completion(request_fixture, config_fixture, trace_id="test_trace_id"):
                responses.append(resp)
    
    @pytest.mark.asyncio
    async def test_chat_completion_raise_exception_capture_response(
        self, mock_inits_and_import_chat_completion, request_fixture, config_fixture, mocker
    ):
        chat_completion, mock_core_bots, mock_chat, *_ = mock_inits_and_import_chat_completion
        
        # Setup main response stream
        mock_response_data = ["response1", "response2"]
        mock_engine = mocker.MagicMock()
        mock_engine = await self.setup_mock_stream(mock_engine, mock_response_data, KeyError)
        mock_chat.ConversationEngine.return_value = mock_engine

        # Setup exception response
        mock_exception_data = ["exception_response2"]
        mock_lambot = mocker.MagicMock()
        mock_core_bots.LamBot.return_value = mock_lambot
        
        mock_exception_response = mocker.MagicMock()
        async def mock_exception_stream_response(*args, **kwargs):
            for item in mock_exception_data:
                yield item
        mock_exception_response.stream_response = mock_exception_stream_response
        mock_core_bots.ExceptionAssistBot.return_value = mock_exception_response

        responses = []
        async for resp in chat_completion(request_fixture, config_fixture, trace_id="test_trace_id"):
            responses.append(resp)
            
        assert len(responses) == 2
        assert mock_core_bots.ExceptionAssistBot.call_count == 1
        assert mock_lambot.metric_api_client.make_async_log_exceptions_request.call_count == 1

