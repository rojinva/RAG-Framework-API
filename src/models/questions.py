from pydantic import BaseModel, Field
from typing import List


class SuggestedQuestions(BaseModel):
    suggested_questions: List[str] = Field(
        min_items=3,
        max_items=3,
        description="list of three suggested follow-up questions",
    )
