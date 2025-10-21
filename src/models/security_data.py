from typing import List
from pydantic import BaseModel
from fastapi.security import HTTPAuthorizationCredentials


class SecurityData(BaseModel):
    """
    Pydantic model for security data returned by get_security_data.
    
    Attributes:
        security_groups (List[str]): List of security group IDs the user belongs to.
        user_role (str): The user's role (admin, user, or custom).
        bearer_token (HTTPAuthorizationCredentials): The original bearer token for downstream use.
    """
    security_groups: List[str]
    user_role: str
    bearer_token: HTTPAuthorizationCredentials
