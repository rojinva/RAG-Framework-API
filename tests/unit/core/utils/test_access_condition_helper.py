import os
import sys
# Adjust the path to include the parent directory
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))), "src"))
import pytest
from unittest.mock import patch

@pytest.fixture
def mock_inits_and_import_ach(mocker):
    with patch.dict('sys.modules', {
        "dotenv": mocker.MagicMock(),
        "dotenv.load_dotenv": mocker.MagicMock(),
        'src.core.bots.lambot': mocker.MagicMock(),
        'src.core.base': mocker.MagicMock(),
        'src.core.utils.converters': mocker.MagicMock(),
        "src.core.retrievers": mocker.MagicMock(),
        "src.core.retrievers.multi_retriever": mocker.MagicMock(),
        "src.core.retrievers.retriever": mocker.MagicMock(),
    }):
        import src.core.utils.access_condition_helper as access_condition_helper
        yield access_condition_helper

class TestAccessConditionChecks:

    def test_access_conditions_not_in_lambot_config(self, mock_inits_and_import_ach):
        access_condition_helper = mock_inits_and_import_ach
        lambot_config = {'display_name':'name'}
        with pytest.raises(ValueError, match=f"access_conditions not found in LamBot config {lambot_config['display_name']}"):
            access_condition_helper.access_condition_checks(lambot_config, [], [])


    def test_additional_required_security_groups_not_met(self, mock_inits_and_import_ach, mocker):
        access_condition_helper = mock_inits_and_import_ach
        mock_check_additional_required_security_groups = mocker.patch.object(access_condition_helper, 'check_additional_required_security_groups', return_value=False)
        lambot_config = {
            'display_name': 'name',
            'access_conditions': {
                'additional_required_security_groups': [{'id': 'group1'}],
                'required_tools': [],
                'min_tools': 0
            }
        }
        security_group_memberships_list = []
        tool_access_list = []
        assert not access_condition_helper.access_condition_checks(lambot_config, security_group_memberships_list, tool_access_list)
        assert mock_check_additional_required_security_groups.called
    

    def test_additional_required_security_groups_met(self, mock_inits_and_import_ach, mocker):
        access_condition_helper = mock_inits_and_import_ach
        mock_check_additional_required_security_groups = mocker.patch.object(access_condition_helper, 'check_additional_required_security_groups', return_value=True)
        lambot_config = {
            'display_name': 'name',
            'access_conditions': {
                'additional_required_security_groups': [{'id': 'group1'}],
                'required_tools': [],
                'min_tools': 0
            }
        }
        security_group_memberships_list = ['group1']
        tool_access_list = []
        assert access_condition_helper.access_condition_checks(lambot_config, security_group_memberships_list, tool_access_list)
        assert mock_check_additional_required_security_groups.called


    def test_integration_additional_required_security_groups_not_met(self, mock_inits_and_import_ach, mocker):
        access_condition_helper = mock_inits_and_import_ach
        lambot_config = {
            'display_name': 'name',
            'access_conditions': {
                'additional_required_security_groups': [{'id': 'group1'}],
                'required_tools': [],
                'min_tools': 0
            }
        }
        security_group_memberships_list = ['group2']
        tool_access_list = []
        assert not access_condition_helper.access_condition_checks(lambot_config, security_group_memberships_list, tool_access_list)


    def test_integration_additional_required_security_groups_met(self, mock_inits_and_import_ach, mocker):
        access_condition_helper = mock_inits_and_import_ach
        lambot_config = {
            'display_name': 'name',
            'access_conditions': {
                'additional_required_security_groups': [{'id': 'group1'}],
                'required_tools': [],
                'min_tools': 0
            }
        }
        security_group_memberships_list = ['group1']
        tool_access_list = []
        assert access_condition_helper.access_condition_checks(lambot_config, security_group_memberships_list, tool_access_list)


    def test_required_tools_not_met(self, mock_inits_and_import_ach, mocker):
        access_condition_helper = mock_inits_and_import_ach
        mock_check_required_tools = mocker.patch.object(access_condition_helper, 'check_required_tools', return_value=False)
        lambot_config = {
            'display_name': 'name',
            'access_conditions': {
                'additional_required_security_groups': [],
                'required_tools': ['tool1'],
                'min_tools': 0
            }
        }
        security_group_memberships_list = []
        tool_access_list = ['tool2']
        assert not access_condition_helper.access_condition_checks(lambot_config, security_group_memberships_list, tool_access_list)
        assert mock_check_required_tools.called

    
    def test_required_tools_met(self, mock_inits_and_import_ach, mocker):
        access_condition_helper = mock_inits_and_import_ach
        mock_check_required_tools = mocker.patch.object(access_condition_helper, 'check_required_tools', return_value=True)
        lambot_config = {
            'display_name': 'name',
            'access_conditions': {
                'additional_required_security_groups': [],
                'required_tools': ['tool1'],
                'min_tools': 0
            }
        }
        security_group_memberships_list = []
        tool_access_list = ['tool2']
        assert access_condition_helper.access_condition_checks(lambot_config, security_group_memberships_list, tool_access_list)
        assert mock_check_required_tools.called


    def test_integration_required_tools_not_met(self, mock_inits_and_import_ach, mocker):
        access_condition_helper = mock_inits_and_import_ach
        lambot_config = {
            'display_name': 'name',
            'access_conditions': {
                'additional_required_security_groups': [],
                'required_tools': ['tool1'],
                'min_tools': 0
            }
        }
        security_group_memberships_list = []
        tool_access_list = ['tool2']
        assert not access_condition_helper.access_condition_checks(lambot_config, security_group_memberships_list, tool_access_list)


    def test_integration_required_tools_met(self, mock_inits_and_import_ach, mocker):
        access_condition_helper = mock_inits_and_import_ach
        lambot_config = {
            'display_name': 'name',
            'access_conditions': {
                'additional_required_security_groups': [],
                'required_tools': ['tool1'],
                'min_tools': 0
            }
        }
        security_group_memberships_list = []
        tool_access_list = ['tool1']
        assert access_condition_helper.access_condition_checks(lambot_config, security_group_memberships_list, tool_access_list)


    def test_min_tools_not_met(self, mock_inits_and_import_ach, mocker):
        access_condition_helper = mock_inits_and_import_ach
        mock_check_min_tools = mocker.patch.object(access_condition_helper, 'check_min_tools', return_value=False)
        lambot_config = {
            'display_name': 'name',
            'access_conditions': {
                'additional_required_security_groups': [],
                'required_tools': [],
                'min_tools': 2
            }
        }
        security_group_memberships_list = []
        tool_access_list = ['tool1']
        assert not access_condition_helper.access_condition_checks(lambot_config, security_group_memberships_list, tool_access_list)
        assert mock_check_min_tools.called    


    def test_min_tools_met(self, mock_inits_and_import_ach, mocker):
        access_condition_helper = mock_inits_and_import_ach
        mock_check_min_tools = mocker.patch.object(access_condition_helper, 'check_min_tools', return_value=True)
        lambot_config = {
            'display_name': 'name',
            'access_conditions': {
                'additional_required_security_groups': [],
                'required_tools': [],
                'min_tools': 2
            }
        }
        security_group_memberships_list = []
        tool_access_list = ['tool1', 'tool2']
        assert access_condition_helper.access_condition_checks(lambot_config, security_group_memberships_list, tool_access_list)
        assert mock_check_min_tools.called


    def test_integration_min_tools_not_met(self, mock_inits_and_import_ach, mocker):
        access_condition_helper = mock_inits_and_import_ach
        lambot_config = {
            'display_name': 'name',
            'access_conditions': {
                'additional_required_security_groups': [],
                'required_tools': [],
                'min_tools': 2
            },
            'tools': ['tool1', 'tool2']
        }
        security_group_memberships_list = []
        tool_access_list = ['tool1']
        assert not access_condition_helper.access_condition_checks(lambot_config, security_group_memberships_list, tool_access_list)

    
    def test_integration_min_tools_met(self, mock_inits_and_import_ach, mocker):
        access_condition_helper = mock_inits_and_import_ach
        lambot_config = {
            'display_name': 'name',
            'access_conditions': {
                'additional_required_security_groups': [],
                'required_tools': [],
                'min_tools': 2
            },
            'tools': ['tool1', 'tool2']
        }
        security_group_memberships_list = []
        tool_access_list = ['tool1', 'tool2']
        assert access_condition_helper.access_condition_checks(lambot_config, security_group_memberships_list, tool_access_list)


    def test_integration_min_tools_all_met(self, mock_inits_and_import_ach, mocker):
        access_condition_helper = mock_inits_and_import_ach
        lambot_config = {
            'display_name': 'name',
            'access_conditions': {
                'additional_required_security_groups': [],
                'required_tools': [],
                'min_tools': 'all'
            },
            'tools': ['tool1', 'tool2', 'tool3']
        }
        security_group_memberships_list = []
        tool_access_list = ['tool1', 'tool2', 'tool3']
        assert access_condition_helper.access_condition_checks(lambot_config, security_group_memberships_list, tool_access_list)


    def test_integration_min_tools_all_not_met(self, mock_inits_and_import_ach, mocker):
        access_condition_helper = mock_inits_and_import_ach
        lambot_config = {
            'display_name': 'name',
            'access_conditions': {
                'additional_required_security_groups': [],
                'required_tools': [],
                'min_tools': 'all'
            },
            'tools': ['tool1', 'tool2', 'tool3']
        }
        security_group_memberships_list = []
        tool_access_list = ['tool1', 'tool2']
        assert not access_condition_helper.access_condition_checks(lambot_config, security_group_memberships_list, tool_access_list)


    def test_all_conditions_met(self, mock_inits_and_import_ach, mocker):
        access_condition_helper = mock_inits_and_import_ach
        mock_check_additional_required_security_groups = mocker.patch.object(access_condition_helper, 'check_additional_required_security_groups', return_value=True)
        mock_check_required_tools = mocker.patch.object(access_condition_helper, 'check_required_tools', return_value=True)
        mock_check_min_tools = mocker.patch.object(access_condition_helper, 'check_min_tools', return_value=True)

        lambot_config = {
            'display_name': 'name',
            'access_conditions': {
                'additional_required_security_groups': [{'id': 'group1'}],
                'required_tools': ['tool1'],
                'min_tools': 2
            }
        }
        security_group_memberships_list = ['group1']
        tool_access_list = ['tool1', 'tool2']

        assert access_condition_helper.access_condition_checks(lambot_config, security_group_memberships_list, tool_access_list)
        assert mock_check_additional_required_security_groups.called
        assert mock_check_required_tools.called
        assert mock_check_min_tools.called


class TestCheckAdditionalRequiredSecurityGroups:
    def test_additional_required_security_groups_met(self, mock_inits_and_import_ach):
        access_condition_helper = mock_inits_and_import_ach
        lambot_config = {
            'access_conditions': {
                'additional_required_security_groups': [{'id': 'group1'}, {'id': 'group2'}]
            }
        }
        security_group_memberships_list = ['group1', 'group2']
        assert access_condition_helper.check_additional_required_security_groups(lambot_config, security_group_memberships_list)

    def test_additional_required_security_groups_not_met(self, mock_inits_and_import_ach):
        access_condition_helper = mock_inits_and_import_ach
        lambot_config = {
            'access_conditions': {
                'additional_required_security_groups': [{'id': 'group1'}, {'id': 'group2'}]
            }
        }
        security_group_memberships_list = ['group1']
        assert not access_condition_helper.check_additional_required_security_groups(lambot_config, security_group_memberships_list)


class TestCheckRequiredTools:
    def test_required_tools_met(self, mock_inits_and_import_ach):
        access_condition_helper = mock_inits_and_import_ach
        lambot_config = {
            'access_conditions': {
                'required_tools': ['tool1', 'tool2']
            }
        }
        tool_access_list = ['tool1', 'tool2', 'tool3']
        assert access_condition_helper.check_required_tools(lambot_config, tool_access_list)

    def test_required_tools_not_met(self, mock_inits_and_import_ach):
        access_condition_helper = mock_inits_and_import_ach
        lambot_config = {
            'access_conditions': {
                'required_tools': ['tool1', 'tool2']
            }
        }
        tool_access_list = ['tool1']
        assert not access_condition_helper.check_required_tools(lambot_config, tool_access_list)


class TestCheckMinTools:
    def test_min_tools_met(self, mock_inits_and_import_ach):
        access_condition_helper = mock_inits_and_import_ach
        lambot_config = {
            'access_conditions': {
                'min_tools': 2
            },
            'tools': ['tool1', 'tool2', 'tool3']
        }
        tool_access_list = ['tool1', 'tool2']
        assert access_condition_helper.check_min_tools(lambot_config, tool_access_list)

    def test_min_tools_not_met(self, mock_inits_and_import_ach):
        access_condition_helper = mock_inits_and_import_ach
        lambot_config = {
            'access_conditions': {
                'min_tools': 2
            },
            'tools': ['tool1', 'tool2', 'tool3']
        }
        tool_access_list = ['tool1']
        assert not access_condition_helper.check_min_tools(lambot_config, tool_access_list)

    def test_min_tools_all_met(self, mock_inits_and_import_ach):
        access_condition_helper = mock_inits_and_import_ach
        lambot_config = {
            'access_conditions': {
                'min_tools': 'all'
            },
            'tools': ['tool1', 'tool2', 'tool3']
        }
        tool_access_list = ['tool1', 'tool2', 'tool3']
        assert access_condition_helper.check_min_tools(lambot_config, tool_access_list)

    def test_min_tools_all_not_met(self, mock_inits_and_import_ach):
        access_condition_helper = mock_inits_and_import_ach
        lambot_config = {
            'access_conditions': {
                'min_tools': 'all'
            },
            'tools': ['tool1', 'tool2', 'tool3']
        }
        tool_access_list = ['tool1', 'tool2']
        assert not access_condition_helper.check_min_tools(lambot_config, tool_access_list)
