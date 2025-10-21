from datetime import datetime
from pydantic import BaseModel, Field

current_date = datetime.now().strftime("%B %d, %Y")


class SearchInput(BaseModel):
    """Input to the retriever."""

    query: str = Field(
        description=f"The search query that will be sent to the Bing Search tool for information retrieval. Ensure that the query includes the current date ({current_date}) to get the most relevant results."
    )
