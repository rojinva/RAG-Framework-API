from dotenv import load_dotenv

load_dotenv(override=True)
from src.models import LamBotChatRequest, LamBotConfig, SecurityData, UserRole
from fastapi import Depends, Header, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src.core.database.lambot import LamBotMongoDB
from src.core.utils.auth_helpers import get_entra_id_security_groups, get_user_role, get_user_info
from src.models.config import ToolConfig
from src.core.utils.log_trace import log_trace_event
from typing import List
from src.models.functions import datetime_now
from src.core.context.vars import user_email_var
from uuid import uuid4

security = HTTPBearer()


# New shared dependency that fetches security data once per request
def get_security_data(
    bearer_token: HTTPAuthorizationCredentials = Depends(security),
    custom_user_role: str = Header(None, alias="CUSTOM-USER-ROLE")
) -> SecurityData:
    """
    Shared dependency that gets security groups and user role once per request.
    
    Args:
        bearer_token: The bearer token containing the user's credentials
        custom_user_role: Optional header to override the user's role
        
    Returns:
        SecurityData: Object containing security groups and user role
    """    
    return fetch_security_data(bearer_token, custom_user_role)

def get_security_data_external(
    request: Request,
    bearer_token: HTTPAuthorizationCredentials = Depends(security),
    custom_user_role: str = Header(None, alias="CUSTOM-USER-ROLE")
) -> SecurityData:
    """
    Shared dependency that gets security groups and user role once per request.
    
    Args:
        bearer_token: The bearer token containing the user's credentials
        custom_user_role: Optional header to override the user's role
        
    Returns:
        SecurityData: Object containing security groups and user role
    """  

    graph_token = request.headers.get("graph-token")
    if graph_token:
        bearer_token = HTTPAuthorizationCredentials(scheme="Bearer", credentials=graph_token)
    return fetch_security_data(bearer_token, custom_user_role)
    
def fetch_security_data(bearer_token: HTTPAuthorizationCredentials ,
    custom_user_role: str = Header(None, alias="CUSTOM-USER-ROLE")
) -> SecurityData:
    """
     gets security groups for user and role per request.
    
    Args:
        bearer_token: The bearer token containing the user's credentials
        custom_user_role: Optional header to override the user's role
        
    Returns:
        SecurityData: Object containing security groups and user role
    """
    
    security_group_memberships_list = get_entra_id_security_groups(
        bearer_token.credentials
    )
    
    user_role = get_user_role(security_group_memberships_list)
    
    if user_role == UserRole.UNAUTHORIZED:
        raise HTTPException(
            status_code=401,
            detail="The user is not authorized to access this endpoint.",
        )
    
    # If an admin has downgraded their role through a header, then downgrade here
    if user_role == UserRole.ADMIN and custom_user_role:
        user_role = custom_user_role
    
    return SecurityData(
        security_groups=security_group_memberships_list,
        user_role=user_role,
        bearer_token=bearer_token,  # Pass token through for other dependencies that might need it
    )

def verify_api_access(
    request: Request,
    lambot_chat_request: LamBotChatRequest,
    security_data: SecurityData = Depends(get_security_data)
) -> LamBotConfig:
    """
    Verifies API access for a given LamBot chat request based on user roles and security group memberships.
    Args:
        lambot_chat_request (LamBotChatRequest): The chat request containing the LamBot ID.
        security_data (SecurityData): Security data including user role and security groups.
    Returns:
        LamBotConfig: The configuration of the requested LamBot.
    Raises:
        HTTPException:
            - 404: If the requested LamBot configuration is not found.
            - 401: If the user does not have access to the required tools.
            - 403 : If the user does not have access to a personal LamBot configuration.
    """

    lambot = fetch_lambot_config(request, lambot_chat_request, security_data)
    verify_personal_lambot_access(lambot)
    return lambot

def verify_api_access_external(
    request: Request,
    lambot_chat_request: LamBotChatRequest,
    security_data: SecurityData = Depends(get_security_data_external)
) -> LamBotConfig:
    """
    Verifies API access for a given LamBot chat request based on user roles and security group memberships.
    Args:
        lambot_chat_request (LamBotChatRequest): The chat request containing the LamBot ID.
        security_data (SecurityData): Security data including user role and security groups.
    Returns:
        LamBotConfig: The configuration of the requested LamBot.
    Raises:
        HTTPException:
            - 404: If the requested LamBot configuration is not found.
            - 403 : If the user does not have access to a personal LamBot configuration.
    """

    lambot = fetch_lambot_config(request, lambot_chat_request, security_data)
    verify_personal_lambot_access(lambot)
    return lambot

def fetch_lambot_config(request: Request,
    lambot_chat_request: LamBotChatRequest,
    security_data: SecurityData )-> LamBotConfig:
    """
    Verifies API access for a given LamBot request based on roles and security group memberships.
    Args:
        lambot_chat_request (LamBotChatRequest): The chat request containing the LamBot ID.
        security_data (SecurityData): Security data including user role and security groups.
    Returns:
        LamBotConfig: The configuration of the requested LamBot.
    Raises:
        HTTPException:
            - 404: If the requested LamBot configuration is not found.
            - 401: If the user does not have access to the required tools.
    """
    lambot_db = LamBotMongoDB.get_instance()

    user_role = security_data.user_role
    security_group_memberships_list = security_data.security_groups

    lambot_config = lambot_db.lambot_config_db.fetch_lambot(
        lambot_id=lambot_chat_request.lambot_id, 
        user_role=user_role, 
        security_group_list=security_group_memberships_list
    )
    if not lambot_config:
        raise HTTPException(
            status_code=404,
            detail="The requested LamBot Config could not be found in the MongoDB collection",
        )
    
    lambot_tool_names_list = [tool.name for tool in lambot_config.tools]
    if lambot_tool_names_list:
        accessible_tools_list = lambot_db.tool_config_db.fetch_all_tools(
            user_role, security_group_memberships_list
        )

        tool_names_list = [tool.name for tool in accessible_tools_list]

        if not set(lambot_tool_names_list).issubset(set(tool_names_list)):
            raise HTTPException(
                status_code=401,
                detail=f"The user does not have access to {set(lambot_tool_names_list) - set(tool_names_list)}",
            )
        
    trace_id = request.headers.get("x-trace-id")
    
    log_trace_event(
        trace_id=trace_id,
        step="security_check_passed",
    )

    return lambot_config

def fetch_all_tools_security_check(
    security_data: SecurityData = Depends(get_security_data)
) -> List[ToolConfig]:
    """
    Returns a list of tool configs the user has access to based on their security group memberships.

    Args:
        security_data (SecurityData): Security data including user role and security groups.

    Returns:
        List[ToolConfig]: A list of tool configs the user has access to.
    """
    lambot_db = LamBotMongoDB.get_instance()
    
    user_role = security_data.user_role
    security_group_memberships_list = security_data.security_groups

    accessible_tools_configs_list = lambot_db.tool_config_db.fetch_all_tools(user_role, security_group_memberships_list)
    
    return accessible_tools_configs_list

def lambots_admin_check(
    security_data: SecurityData = Depends(get_security_data)
):
    """
    Checks if the user is an admin.
    Args:
        security_data (SecurityData): Security data including user role and security groups.
    Raises:
        HTTPException: If the user is not an admin.
    Returns:
        None
    """
    print("lambots_admin_check: Start checking if the user is an admin...")    
    user_role = security_data.user_role

    if user_role != UserRole.ADMIN:
        raise HTTPException(
            status_code=401,
            detail="The user is not authorized to access this endpoint. Only members of Lambots.Admins can use this endpoint.",
        )
    
    print("lambots_admin_check: Finished checking if the user is an admin successfully.")
    
def lambots_user_check(
    security_data: SecurityData = Depends(get_security_data)
):
    """
    Checks if the user is part of the Lambots.Users security group
    Args:
        security_data (SecurityData): Security data including user role and security groups.
    Raises:
        HTTPException: If the user is not authorized to access the endpoint.
    Returns:
        None
    """
    print("lambots_user_check: Start checking if the user is a Lambots.User...")    
    user_role = security_data.user_role
    
    # This check is redundant now since unauthorized users are caught in get_security_data,
    # but keeping it for explicitness and compatibility
    if user_role == UserRole.UNAUTHORIZED:
        raise HTTPException(
            status_code=401,
            detail="The user is not authorized to access this endpoint. Only members of Lambots.Users can use this endpoint.",
        )
    print("lambots_user_check: Finished checking if the user is a Lambots.User successfully.")


def get_user_email_from_security_data(
    security_data: SecurityData = Depends(get_security_data)
) -> str:
    """
    Extracts the user's email from the bearer token.
    
    Args:
        security_data (SecurityData): Security data including bearer token
        
    Returns:
        str: The user's email address
        
    Raises:
        HTTPException: If unable to extract email from token
    """
    try:
        # Use the existing get_user_info function to extract user details
        user_info = get_user_info(security_data.bearer_token.credentials)
        
        user_email = user_info.get('email')
        
        if not user_email:
            raise HTTPException(
                status_code=400,
                detail="Unable to extract user email from authentication token"
            )
            
        return user_email
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error extracting user email: {str(e)}"
        )

async def transform_request_payload_to_lambot_config(
    request: Request,
    security_data: SecurityData = Depends(get_security_data),
    id: str = None
) -> LamBotConfig:
    """
    Transform the raw request data into a LamBotConfig with all necessary pre-validation changes.

    This funnction allows us to take an incomplete LamBotConfig and add all the necessary server
    side transformations to it before validation.

    We use this in POST and PUT. This is meant to pass pydantic validation ensuring a valid object can
    be inserted into the database. Validation of correct data is done in a different function
    """
    # Get the raw JSON data from the request
    raw_data = await request.json()

    # Extract user email from the bearer token
    try:
        user_info = get_user_info(security_data.bearer_token.credentials)
        user_email = user_info.get('email')
        
        if not user_email:
            raise HTTPException(status_code=400, detail="Unable to extract user email from authentication token")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error extracting user email: {str(e)}")
    
    # Apply pre-validation transformations
    current_time = datetime_now()
    
    # Set creator and timestamps
    raw_data['creator'] = user_email
    
    if not raw_data.get('creation_date'):
        raw_data['creation_date'] = current_time
    raw_data['last_modified_date'] = current_time

    ui_components = raw_data.get('ui_components', {})
    if not isinstance(ui_components, dict):
        raise HTTPException(status_code=400, detail="ui_components must be a dictionary")
    raw_data['ui_components'] = ui_components

    raw_data["conversation_starters"] = raw_data.get('conversation_starters', [])

    
    # Generate UUID if not provided
    if 'id' not in raw_data or not raw_data['id']:
        raw_data['id'] = str(uuid4())
    
    # Set default API version if not provided
    if 'api_version' not in raw_data or not raw_data['api_version']:
        raw_data['api_version'] = "1.0"  # Set your default API version
    
    # Ensure personal flag is set
    raw_data['personal'] = True
    
    # Add any other pre-validation transformations here as needed
    # Example: Set default values, normalize data, etc.
    
    # Create and validate the LamBotConfig
    try:
        lambot_config = LamBotConfig(**raw_data)
        return lambot_config
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Validation error: {str(e)}")
    

def verify_personal_lambot_access(
    lambot_config: LamBotConfig,
):
    """
    Check if the user has access to a personal LamBot.
    
    Args:
        lambot_config (LamBotConfig): The LamBot configuration to check.
        
    Raises:
        HTTPException: If the user does not have access to the personal LamBot.
    """
    if not lambot_config.personal:
        return
        
    current_user_email = user_email_var.get("email").lower()
    
    # Check ownership logic:
    # 1. If owner exists and is not empty, it must match current user (takes precedence)
    # 2. If no owner is set, check creator field
    if lambot_config.owner and lambot_config.owner.strip() != "":
        # Owner field exists and has value, it takes precedence
        if lambot_config.owner.lower() != current_user_email:
            raise HTTPException(
                status_code=403, 
                detail="You are not the owner of this personal LamBot configuration"
            )
    else:
        # No owner set, fall back to creator check
        if lambot_config.creator.lower() != current_user_email:
            raise HTTPException(
                status_code=403, 
                detail="You are not the creator of this personal LamBot configuration"
            )

