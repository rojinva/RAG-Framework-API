from pydantic import Field
from src.models.base import ConfiguredBaseModel

class IntermediateStep(ConfiguredBaseModel):
    message: str = Field(..., description="Intermediate step message from tool execution")

    def __hash__(self):
        return hash(self.message)  # Hash based on message

    def __eq__(self, other):
        if isinstance(other, IntermediateStep):
            return self.message == other.message  # Equality based on message
        return False
   


