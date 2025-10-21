import os
import sys
# Adjust the path to include the parent directory
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "src"))
import json
import pytest
from uuid import uuid4
from unittest.mock import patch 
from fastapi import FastAPI, Request, Depends, Header
from fastapi.testclient import TestClient
from src.models.config import LanguageModelConfig
from src.models.access_conditions import AccessConditions
from src.models.citation import Citation
from src.models import LamBotChatRequest, LamBotConfig, SecurityData, QueryConfig, LamBotChatResponse


async def mock_chat_completion_stream_response(lambot_chat_request: LamBotChatRequest, lambot_config: LamBotConfig, trace_id: str,):
    chat_response = LamBotChatResponse(
        chunk="sample text chunk",
        citations = [Citation(
            origin= "tool-name",
            display_name="display-name",
            is_used=True,
            displayNumber=1,
            )],
        done=True
    )
    yield chat_response.model_dump_json() + "\n"


async def mock_chat_completion_stream_multi_response(lambot_chat_request: LamBotChatRequest, lambot_config: LamBotConfig, trace_id: str,):
    
    chunks = ["I am chunk 1", "I am chunk 2"]
    for chunk in chunks:
        chat_response = LamBotChatResponse(
            chunk=chunk,
            citations = [Citation(
                origin= "tool-name",
                display_name="display-name",
                is_used=True,
                displayNumber=1,
                )],
            done=True
        )

        yield chat_response.model_dump_json() + "\n"


class TestChatCompletion:

    @pytest.fixture
    def setup_mock_imports(self, mocker):
        
        mock_chat_completion = mocker.MagicMock()
        mock_chat_completion.chat_completion = mock_chat_completion_stream_response
        q_config = QueryConfig(
            system_message="You are a helpful assistant.",
            temperature=0.7,
            selected_tools=[],
            language_model=LanguageModelConfig(
                name="gpt-4o-mini-not-real",
                deployment_name="gpt-4o-mini-not-real",
                display_name="GPT-4o Mini",
                description="A smaller version of GPT-4 optimized for speed and efficiency.",
                unsupported_features=[]
            ),
            top_k=5,
            force_tool_call=False
        ) 
        lambot_config = LamBotConfig(
            id=uuid4(), 
            display_name="Test Bot",
            description="A test bot",
            creator="test_creator",
            api_version="1.0",
            defaultQueryConfig=q_config,
            tools = [],
            agent="tool_calling",
            conversation_starters=[],
            combine_retriever_tools=False,
            suggest_followup_questions=False,
            supported_language_models=[],
            access_conditions=AccessConditions(
                min_tools=0,
                required_tools=[],
                additional_required_security_groups=[]),
            )
        mock_verify = mocker.MagicMock()
        mock_verify.return_value = lambot_config
        mock_endpoint_dependencies = mocker.MagicMock()
        mock_endpoint_dependencies.verify_api_access = mock_verify
        mock_log_trace_event = mocker.MagicMock()
        mock_log_trace = mocker.MagicMock()
        mock_log_trace.log_trace_event = mock_log_trace_event
        with patch.dict('sys.modules', {
            'dotenv.load_dotenv': mocker.MagicMock(),
            "src.core.utils.endpoint_dependencies": mock_endpoint_dependencies,
            'src.core.bots': mocker.MagicMock(),
            'src.core.bots.lambot': mocker.MagicMock(),
            'src.core.utils.log_trace': mock_log_trace,
            }):
            yield mock_verify, mock_log_trace_event

    @pytest.fixture
    def chat_completion_single_message(self, setup_mock_imports, mocker):
        mock_verify, mock_log_trace_event = setup_mock_imports
        mock_chat_completion = mocker.MagicMock()
        mock_chat_completion.chat_completion = mock_chat_completion_stream_response
        with patch.dict('sys.modules', {
            'src.services.chat_completion_service': mock_chat_completion,}):
            from src.routes.chat_completion import chat_router
            app = FastAPI(title="LamBots API")
            app.include_router(chat_router)
            yield TestClient(app), mock_verify, mock_log_trace_event

    @pytest.fixture
    def chat_completion_multi_message(self, setup_mock_imports, mocker):
        mock_verify, mock_log_trace_event = setup_mock_imports
        mock_chat_completion = mocker.MagicMock()
        mock_chat_completion.chat_completion = mock_chat_completion_stream_multi_response
        with patch.dict('sys.modules', {
            'src.services.chat_completion_service': mock_chat_completion,}):
            from src.routes.chat_completion import chat_router
            app = FastAPI(title="LamBots API")
            app.include_router(chat_router)
            yield TestClient(app), mock_verify, mock_log_trace_event


    def test_post_chat_completion(self, chat_completion_single_message):
        app, mock_verify, mock_log_trace_event = chat_completion_single_message
        request_data = LamBotChatRequest(
            lambot_id="lambot_id",
            query={"kwargs": {}},
            messages=[
            {
                "role": "user",
                "content": "Hello, how are you?"
            }
            ]
        )
        response = app.post(
            "/chat/chat_completion/",
            data=request_data.model_dump_json(),
            params={"args": None, "kwargs": None},
            headers={"x-trace-id": "test_trace_id"},
        )
        response_json = response.json()
        
        assert response.status_code == 200
        assert response_json["chunk"] == "sample text chunk"
        assert mock_verify.call_count == 1
        assert mock_log_trace_event.call_count == 1


    def test_post_chat_completion_multi_chunk(self, chat_completion_multi_message):
        app, mock_verify, mock_log_trace_event = chat_completion_multi_message
        request_data = LamBotChatRequest(
            lambot_id="lambot_id",
            query={"kwargs": {}},
            messages=[
            {
                "role": "user",
                "content": "Hello, how are you?"
            }
            ]
        )
        response = app.post(
            "/chat/chat_completion/",
            data=request_data.model_dump_json(),
            params={"args": None, "kwargs": None},
            headers={"x-trace-id": "test_trace_id"},
        )
        response_list = [json.loads(i) for i in response.text.split("\n") if i != '']

        assert response.status_code == 200
        assert len(response_list) == 2
        assert mock_verify.call_count == 1
        assert mock_log_trace_event.call_count == 1
