import requests
import logging
from typing import List
from dotenv import load_dotenv
load_dotenv(override=True)

import os
from src.core.cache.decorators import cache_user
from src.models.retriever_tool import AccessControlParam

logger = logging.getLogger(__name__)


def get_user_info(access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # Using $select to specify the attributes you want to retrieve
    params = {"$select": "onPremisesSamAccountName,mail"}
    response = requests.get(
        "https://graph.microsoft.com/v1.0/me", headers=headers, params=params
    )

    if response.status_code != 200:
        raise PermissionError("Failed to fetch user information from Microsoft Graph API")
    
    response_json = response.json()
    onprem_sam_account_name = response_json.get("onPremisesSamAccountName")
    email = response_json.get("mail")

    return {
        AccessControlParam.USERNAME: onprem_sam_account_name,
        AccessControlParam.EMAIL: email,
        AccessControlParam.ACCESS_TOKEN: access_token
    }

@cache_user("entra_id_security_groups")
def get_entra_id_security_groups(access_token):
    
    # If not in cache, make the API call
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # Using $select to specify the attributes you want to retrieve
    response = requests.get(
        "https://graph.microsoft.com/v1.0/me/transitiveMemberOf?$top=998", headers=headers)

    if response.status_code != 200:
        raise PermissionError("Failed to fetch user information from Microsoft Graph API")

    response_json = response.json()
    security_groups = [group['id'] for group in response_json['value']]
    
    return security_groups

def get_user_role(security_group_list: List[str]) -> str:
    required_env_vars = [
            "LAMBOTS_ADMIN_ID",
            "LAMBOTS_CREATOR_ID",
            "LAMBOTS_USER_ID",
        ]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

    if os.getenv('LAMBOTS_ADMIN_ID') in security_group_list:
        return "admin"
    elif os.getenv('LAMBOTS_CREATOR_ID') in security_group_list:
        return "creator"
    elif os.getenv('LAMBOTS_USER_ID') in security_group_list:
        return "user"
    else:
        return "unauthorized"
    

