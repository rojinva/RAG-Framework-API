from pydantic import BaseModel, Field, validator
from typing import List, Union
from src.models.constants import MinimumTools
from src.models.base import ConfiguredBaseModel
    

class SecurityGroup(BaseModel):
    name: str = Field(..., description="The name of the security group")
    id: str = Field(..., description="The object ID of the security group")

class AccessConditions(ConfiguredBaseModel):
    min_tools: Union[int, MinimumTools] = Field(..., description="Minimum number of tools required for access control policy.")
    required_tools: List[str] = Field(..., description="List of required tools for access control policy.")
    additional_required_security_groups: List[SecurityGroup] = Field(..., description="List of additional required security groups for access.")

    @validator("min_tools")
    def validate_min_tools(cls, min_tools):
        if isinstance(min_tools, int) and min_tools < 0:
            raise ValueError("min_tools must be a non-negative integer or 'all'.")
        if isinstance(min_tools, str) and min_tools != "all":
            raise ValueError("min_tools must be a non-negative integer or 'all'.")
        return min_tools
