import os
import sys
# Adjust the path to include the parent directory
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "src"))
import pytest
import mongomock
from unittest.mock import patch


class TestLambotConfigDBServiceFetchAllLambots:

    
    @pytest.fixture()
    def setup_environment(self, mocker):

        with patch.dict('sys.modules', {
            "dotenv": mocker.MagicMock(),
            "dotenv.load_dotenv": mocker.MagicMock(),
            "src.core.utils.mongo_db_interface": mocker.MagicMock(),
            "src.core.utils.mongo_db_interface.MongoDBService": mocker.MagicMock(),
            "src.core.bots.lambot": mocker.MagicMock(),
            "src.core.retrievers": mocker.MagicMock(),
            "src.core.retrievers.multi_retriever": mocker.MagicMock(),
            "src.core.retrievers.retriever": mocker.MagicMock(),
            "src.clients": mocker.MagicMock,
            "src.clients.azure.openai": mocker.MagicMock,
            "src.clients.mongo": mocker.MagicMock,
            "src.clients.langfuse.manager": mocker.MagicMock,
            "src.clients.langfuse.manager_sensitive": mocker.MagicMock,
            "src.clients.langfuse.manager_redacted": mocker.MagicMock,
            "src.clients.synapse": mocker.MagicMock,
            "src.clients.metrics_api_client": mocker.MagicMock,
            "src.clients.redis": mocker.MagicMock,
            "src.core.base": mocker.MagicMock(),
            "src.core.base._document": mocker.MagicMock(),
        }):
            from src.core.database.lambot_config import LamBotConfigDB
            from src.models.constants import LamBotConfigAccessibiltiy
            from src.models.config import ToolConfig, LanguageModelConfig, QueryConfig
            yield LamBotConfigDB, LamBotConfigAccessibiltiy, ToolConfig, LanguageModelConfig, QueryConfig

    @pytest.fixture()
    def setup_mongomock(self):
        """
        Setup fixture to use mongomock for testing MongoDB interactions.
        This will replace the actual MongoDB connection with a mock.
        """
        name = "test_collection"
        mock_mongo_colletion = mongomock.MongoClient().db.create_collection(name=name)
        yield mock_mongo_colletion


    def test_fetch_all_lambots(self, setup_environment, setup_mongomock, mocker):
        # Mock the database connection
        LamBotConfigService, LamBotConfigAccessibiltiy, ToolConfig, LanguageModelConfig, QueryConfig = setup_environment #NOSONAR
        mock_collection = setup_mongomock.lambots

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
        # Mock the find method to return a list of lambots
        mock_collection.find = lambda: [
            {
                "_id": "1",
                "name": "Lambot1",
                "display_name": "Lambot1",
                "tools": ["test_tool"],
                "description": "a test bot",
                "creator": "test_creator",
                "api_version": "1.0",
                "defaultQueryConfig": q_config,
                "agent": "tool_calling",
                "conversation_starters": [],
                "combine_retriever_tools": False,
                "suggest_followup_questions": False,
                "supported_language_models": ["model_name"],
                "default_query_config": {
                    "selected_tools": ["test_tool"],
                    "language_model": "model_name"
                },
                "access_conditions": {
                    'additional_required_security_groups': [{'id': 'group1', "name": "group1"}],
                    'required_tools': ["test_tool"],
                    'min_tools': 1
                }
            },
            {
                "_id": "2",
                "name": "Lambot2",
                "display_name": "Lambot2",
                "tools": ["test_tool"],
                "description": "a test bot",
                "creator": "test_creator",
                "api_version": "1.0",
                "defaultQueryConfig": q_config,
                "agent": "tool_calling",
                "conversation_starters": [],
                "combine_retriever_tools": False,
                "suggest_followup_questions": False,
                "supported_language_models": ["model_name"],
                "default_query_config": {
                    "selected_tools": ["test_tool"],
                    "language_model": "model_name",
                },
                "access_conditions": {
                    'additional_required_security_groups': [{'id': 'group1', "name": "group1"}],
                    'required_tools': ["test_tool"],
                    'min_tools': 1
                }
            }
        ]

        mock_language_model_config = LanguageModelConfig(
            name = "model_name",
            display_name = "display_name",
            descirption = "some description"
        )

        mock_language_model_config_service = mocker.MagicMock()
        mock_language_model_config_service.fetch_all_language_models.return_value = [mock_language_model_config]
        # Mock the service class __init__ method
        mocker.patch.object(LamBotConfigService, '__init__', lambda x: None)
        lambot_config_service = LamBotConfigService()
        lambot_config_service.collection = mock_collection
        lambot_config_service.language_model_config_service = mock_language_model_config_service

        tools = [ToolConfig(
            name="test_tool",
            display_name="test_tool",
            user_has_access=True
        )]
        security_group_memberships_list = ["group1", "group2"]

        # Call the method to fetch all lambots
        result = lambot_config_service.fetch_all_lambots(LamBotConfigAccessibiltiy("accessible"), tools, security_group_memberships_list )

        # Assert that the result matches the expected output
        assert len(result) == 2
        assert result[0].display_name == "Lambot1"
        assert result[1].display_name == "Lambot2"