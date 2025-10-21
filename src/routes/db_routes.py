from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from typing import List, Dict, Any
from src.models.config import LamBotConfig, ToolConfig, LanguageModelConfig, LamBotTransferRequest
from src.models.query_params import LamBotConfigQueryParams
from src.models.constants import LamBotConfigAccessibiltiy
from src.models.security_data import SecurityData
from src.core.utils.endpoint_dependencies import fetch_all_tools_security_check, lambots_admin_check, lambots_user_check, \
    get_security_data, verify_personal_lambot_access, transform_request_payload_to_lambot_config
from src.core.utils.ms_graph_utils import is_valid_graph_email_address
from src.core.database import LamBotMongoDB
from fastapi_pagination import Page, paginate, Params
from src.core.common.exceptions import *

db_router = APIRouter(prefix="/entity")
LAMBOTCONFIG_NOT_FOUND = "LamBotConfig not found"

# making the size 100 for pagination initially so we can support the
# existing frontend that lacks pagination for now
class LamBotsTempParams(Params):
    size: int = 100  # Default page size


@db_router.post(
    "/lambot-config/",
    response_model=Dict[str, Any],
    responses={503: {"detail": "503 error"}},
)
def add_lambot_route(
    lambot_config: LamBotConfig = Depends(transform_request_payload_to_lambot_config),
):
    try:
        return LamBotMongoDB.get_instance().lambot_config_db.add_lambot(lambot_config)
    except AlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))


@db_router.put(
    "/lambot-config/transfer",
    response_model=Dict[str, str],
    responses={503: {"detail": "503 error"}},
)
def transfer_lambot_route(
    transfer_request: LamBotTransferRequest,
    query_params: LamBotConfigQueryParams = Depends(),
    security_data: SecurityData = Depends(get_security_data)
):
    """
    Transfer ownership of a LamBot configuration to a new owner.
    Only allows transfer of personal lambots owned by the requesting owner/creator.
    """
    # Get user role directly from security_data
    user_role = security_data.user_role

    # First, fetch the lambot config using query parameters
    try:
        lambot_config = LamBotMongoDB.get_instance().lambot_config_db.fetch_lambot_by_query_params(
            user_role=user_role,
            security_group_list=security_data.security_groups,
            query_params=query_params
        )
    except NoAccessError as e:
        raise HTTPException(status_code=403, detail=str(e))
    
    if lambot_config is None:
        raise HTTPException(status_code=404, detail=LAMBOTCONFIG_NOT_FOUND)
    
    # Validation checks before transfer
    # Verify the personal field is set to true
    if not lambot_config.personal:
        raise HTTPException(
            status_code=403, 
            detail="Only personal LamBot configurations can be transferred"
        )

    # Verify the current user has access to this personal LamBot (uses same logic as other endpoints)
    verify_personal_lambot_access(lambot_config)

    # Validate that the new owner email exists in Active Directory
    if not is_valid_graph_email_address(transfer_request.new_owner):
        raise HTTPException(
            status_code=400, 
            detail=f"The email address '{transfer_request.new_owner}' does not exist in Active Directory"
        )

    try:
        updated_lambot = LamBotMongoDB.get_instance().lambot_config_db.transfer_lambot_ownership(
            lambot_config.id, 
            transfer_request.new_owner
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return updated_lambot


@db_router.put(
    "/lambot-config/{lambot_id}",
    response_model=LamBotConfig,
    responses={503: {"detail": "503 error"}},
)
def update_lambot_route(
    lambot_id: UUID, 
    lambot_config: LamBotConfig = Depends(transform_request_payload_to_lambot_config),
    tool_configs_list: List[ToolConfig] = Depends(fetch_all_tools_security_check),
    security_data: Dict[str, Any] = Depends(get_security_data)
):
    verify_personal_lambot_access(lambot_config)
    try:
        lambot_config = LamBotMongoDB.get_instance().lambot_config_db.update_lambot(lambot_id, lambot_config, tool_configs_list)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return lambot_config


@db_router.delete(
    "/lambot-config/",
    response_model=bool,
    responses={503: {"detail": "503 error"}},
)
def delete_lambot_route(
    query_params: LamBotConfigQueryParams = Depends(),
    security_data: SecurityData = Depends(get_security_data),
):
    """
    Delete a LamBot configuration based on query parameters.
    Only allows deletion of personal lambots owned by the requesting user.
    """
    # Get user role directly from security_data
    user_role = security_data.user_role


    # First, fetch the lambot config using query parameters
    try:
        lambot_config = LamBotMongoDB.get_instance().lambot_config_db.fetch_lambot_by_query_params(
            user_role=user_role,
            security_group_list=security_data.security_groups,
            query_params=query_params
        )
    except NoAccessError as e:
        raise HTTPException(status_code=403, detail=str(e))
    
    if lambot_config is None:
        raise HTTPException(status_code=404, detail=LAMBOTCONFIG_NOT_FOUND)
    
    # Validation checks before deletion
    # Verify the personal field is set to true
    if not lambot_config.personal:
        raise HTTPException(
            status_code=403, 
            detail="Only personal LamBot configurations can be deleted"
        )

    # Verify the user has access to delete this personal LamBot
    verify_personal_lambot_access(lambot_config)

    # Proceed with deletion using the lambot_id from the found config
    result = LamBotMongoDB.get_instance().lambot_config_db.delete_lambot(lambot_config.id)
    
    # Check if deletion was successful based on the returned message
    if "successfully deleted" not in result.get("message", ""):

        raise HTTPException(status_code=500, detail="Failed to delete LamBot configuration")
    return True


@db_router.get(
    "/lambot-configs/{accessibility}",
    response_model=Page[LamBotConfig],
    responses={503: {"detail": "503 error"}},
)
def fetch_all_lambots_route(
    accessibility: LamBotConfigAccessibiltiy, 
    query_params: LamBotConfigQueryParams = Depends(),
    tool_configs_list: List[ToolConfig] = Depends(fetch_all_tools_security_check), 
    security_data: SecurityData = Depends(get_security_data)
):

    configs = LamBotMongoDB.get_instance().lambot_config_db.fetch_all_lambots(
        accessibility,
        tool_configs_list,
        security_data.security_groups,
        query_params=query_params
    )
    return paginate(configs, params=LamBotsTempParams())


@db_router.get(
    "/lambot-configs/",
    response_model=Page[LamBotConfig],
    responses={503: {"detail": "503 error"}},
)
def fetch_all_lambots_without_accessibility_route(
    query_params: LamBotConfigQueryParams = Depends(),
    tool_configs_list: List[ToolConfig] = Depends(fetch_all_tools_security_check), 
    security_data: SecurityData = Depends(get_security_data)
):

    configs = LamBotMongoDB.get_instance().lambot_config_db.fetch_all_lambots(
        None,  # No accessibility filter
        tool_configs_list, 
        security_data.security_groups,
        query_params=query_params
    )
    return paginate(configs, params=LamBotsTempParams())


@db_router.get(
    "/lambot-config/{lambot_id}",
    response_model=LamBotConfig,
    responses={503: {"detail": "503 error"}},
)
def fetch_lambot_route(
    lambot_id: UUID, 
    tool_configs_list: List[ToolConfig] = Depends(fetch_all_tools_security_check), 
    security_data: SecurityData = Depends(get_security_data)
):
    # Get user role directly from security_data
    user_role = security_data.user_role
    
    try:
        lambot_config = LamBotMongoDB.get_instance().lambot_config_db.fetch_lambot(
            lambot_id=lambot_id,
            user_role=user_role,
            security_group_list=security_data.security_groups
        )
    except NoAccessError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    if lambot_config is None:
        raise HTTPException(status_code=404, detail=LAMBOTCONFIG_NOT_FOUND)

    verify_personal_lambot_access(lambot_config)

    return lambot_config



@db_router.get(
    "/lambot-config/",
    response_model=LamBotConfig,
    responses={503: {"detail": "503 error"}},
)
def fetch_lambot_with_query_params_route(
    query_params: LamBotConfigQueryParams = Depends(),
    security_data: SecurityData = Depends(get_security_data)
):
    """
    Fetch a single LamBot configuration based on query parameters.
    Returns the first accessible config matching the provided filters.
    """
    # Get user role directly from security_data
    user_role = security_data.user_role
    
    try:
        lambot_config = LamBotMongoDB.get_instance().lambot_config_db.fetch_lambot_by_query_params(
            user_role=user_role,
            security_group_list=security_data.security_groups,
            query_params=query_params
        )
    except NoAccessError as e:
        raise HTTPException(status_code=403, detail=str(e))
    
    if lambot_config is None:
        raise HTTPException(status_code=404, detail=LAMBOTCONFIG_NOT_FOUND)
    
    verify_personal_lambot_access(lambot_config)

    return lambot_config

###################################################
# Tool Config Endpoints
###################################################

@db_router.post(
    "/tool-config/",
    response_model=ToolConfig,
    responses={503: {"detail": "503 error"}},
)
def add_tool_route(tool_config: ToolConfig, security_check: None = Depends(lambots_admin_check)):
    try:
        return LamBotMongoDB.get_instance().tool_config_db.add_tool(tool_config)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@db_router.get(
    "/tool-configs/",
    response_model=List[ToolConfig],
    responses={503: {"detail": "503 error"}},
)
def fetch_all_tools_route(tool_configs_list: List[ToolConfig] = Depends(fetch_all_tools_security_check)):
    return tool_configs_list

@db_router.get(
    "/tool-config/{tool_name}",
    response_model=ToolConfig,
    responses={503: {"detail": "503 error"}},
)
def fetch_tool_route(tool_name: str, security_check: None = Depends(lambots_user_check)):
    try:
        return LamBotMongoDB.get_instance().tool_config_db.fetch_tool(tool_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@db_router.delete(
    "/tool-config/{tool_name}",
    response_model=bool,
    responses={503: {"detail": "503 error"}},
)
def delete_tool_route(tool_name: str, security_check: None = Depends(lambots_admin_check)):
    try:
        return LamBotMongoDB.get_instance().tool_config_db.delete_tool(tool_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@db_router.put(
    "/tool-config/{tool_name}",
    response_model=ToolConfig,
    responses={503: {"detail": "503 error"}},
)
def update_tool_route(tool_name: str, tool_config: ToolConfig, security_check: None = Depends(lambots_admin_check)):
    try:
        tool_config = LamBotMongoDB.get_instance().tool_config_db.update_tool(tool_name, tool_config)
        return tool_config
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

###################################################
# Language Model Config Endpoints
###################################################

@db_router.post(
    "/language-model-config/",
    response_model=LanguageModelConfig,
    responses={503: {"detail": "503 error"}},
)
def add_language_model_route(language_model_config: LanguageModelConfig, security_check: None = Depends(lambots_admin_check)):
    try:
        return LamBotMongoDB.get_instance().language_model_config_db.add_language_model(language_model_config)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
@db_router.get(
    "/language-model-configs/",
    response_model=List[LanguageModelConfig],
    responses={503: {"detail": "503 error"}},
)
def fetch_all_language_models_route():
    return LamBotMongoDB.get_instance().language_model_config_db.fetch_all_language_models()

@db_router.get(
    "/language-model-config/{language_model_name}",
    response_model=LanguageModelConfig,
    responses={503: {"detail": "503 error"}},
)
def fetch_language_model_route(language_model_name: str):
    try:
        return LamBotMongoDB.get_instance().language_model_config_db.fetch_language_model(language_model_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
@db_router.delete(
    "/language-model-config/{language_model_name}",
    response_model=bool,
    responses={503: {"detail": "503 error"}},
)
def delete_language_model_route(language_model_name: str, security_check: None = Depends(lambots_admin_check)):
    try:
        return LamBotMongoDB.get_instance().language_model_config_db.delete_language_model(language_model_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
