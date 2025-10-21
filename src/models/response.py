from pydantic import Field
from src.models.base import ConfiguredBaseModel
from src.models.citation import Citation
from src.models.tool import ToolArtifact
from src.models.intermediate_step import IntermediateStep
from typing import List, Optional


class LamBotChatResponse(ConfiguredBaseModel):
    chunk: str = Field(..., description="Streaming chunk from LLM")
    citations: List[Citation] = Field(..., description="Citations")
    followup_questions: Optional[List[str]] = Field(
        None, description="Follow-up questions"
    )
    tool_artifacts: Optional[List[ToolArtifact]] = Field(
        None, description="Tool artifacts"
    )
    intermediate_steps: Optional[List[IntermediateStep]] = Field(
        None, description="Intermediate steps generated during tool execution"
    )
    done: bool = Field(False, description="Signal for whether streaming has completed")


