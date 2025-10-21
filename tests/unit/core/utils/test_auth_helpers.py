import os
import sys
# Adjust the path to include the parent directory
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "src"))
import pytest
from unittest.mock import patch

@pytest.fixture
def mock_lifeservice(mocker):
    # Create a mock module and class
    mock_module = mocker.MagicMock()
    mock_class = mocker.MagicMock()
    mock_module.LifespanServices = mock_class

    # Insert the mock module into sys.modules before import
    with patch.dict('sys.modules', {
        'src.clients.clients': mock_module
    }):
        yield mock_module

class TestGetUserInfo:

    @pytest.fixture
    def mock_requests(self, mocker):
        mock_requests = mocker.MagicMock()
        with patch.dict('sys.modules', {"requests": mock_requests}):
            yield mock_requests
    
    def test_get_user_info_success(self, mock_lifeservice, mock_requests, mocker):
        mock_response = mocker.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "onPremisesSamAccountName": "testuser",
            "mail": "example@email.com"
            }
        mock_requests.get.return_value = mock_response
        from src.core.utils.auth_helpers import get_user_info
        response = get_user_info("test_token")
        assert response == {
            "onPremisesSamAccountName": "testuser",
            "email": "example@email.com"
            }

    
    def test_get_user_info_failed(self, mock_lifeservice, mock_requests, mocker):
        mock_response = mocker.MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {
            "onPremisesSamAccountName": "testuser",
            "mail": "example@email.com"
            }
        mock_requests.get.return_value = mock_response
        from src.core.utils.auth_helpers import get_user_info
        with pytest.raises(PermissionError, match="Failed to fetch user information from Microsoft Graph API"):
            get_user_info("test_token")
        
        