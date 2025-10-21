from typing import List

def access_condition_checks(lambot_config: dict, security_group_memberships_list: List[str], tool_access_list: List[str]) -> bool:

    if "access_conditions" not in lambot_config:
        raise ValueError(f"access_conditions not found in LamBot config {lambot_config['display_name']}")

    if lambot_config['access_conditions']['additional_required_security_groups']:
        if not check_additional_required_security_groups(lambot_config, security_group_memberships_list):
            return False

    if lambot_config['access_conditions']['required_tools']:
        if not check_required_tools(lambot_config, tool_access_list):
            return False

    if lambot_config['access_conditions']['min_tools']:
        if not check_min_tools(lambot_config, tool_access_list):
            return False

    return True

def check_additional_required_security_groups(lambot_config: dict, security_group_memberships_list: List[str]) -> bool:
    for security_group in lambot_config['access_conditions']['additional_required_security_groups']:
        if security_group['id'] not in security_group_memberships_list:
            return False
    return True

def check_required_tools(lambot_config: dict, tool_access_list: List[str]) -> bool:
    for tool in lambot_config['access_conditions']['required_tools']:
        if tool not in tool_access_list:
            return False
    return True

def check_min_tools(lambot_config: dict, tool_access_list: List[str]) -> bool:
    if lambot_config['access_conditions']['min_tools'] == 'all':
        return set(lambot_config['tools']).issubset(set(tool_access_list))
    return lambot_config['access_conditions']['min_tools'] <= len(set(lambot_config['tools']).intersection(set(tool_access_list)))

