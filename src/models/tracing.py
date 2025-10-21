from pydantic import Field
from src.models.base import ConfiguredBaseModel
from datetime import datetime
from src.models.functions import datetime_now


class TraceEvent(ConfiguredBaseModel):
    trace_id: str = Field(..., description="Unique ID for the trace event")
    step: str = Field(..., description="Descriptive name of the trace step")
    timestamp: datetime = Field(
        ..., description="Timestamp of the trace event", default_factory=datetime_now
    )