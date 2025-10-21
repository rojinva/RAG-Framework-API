from typing import Optional
from pydantic import Field
from src.models.config import ConfiguredBaseModel


class ResearchDelegatorConfig(ConfiguredBaseModel):
    language_model_name: str = Field(
        "o3", description="The name of the language model used by the research delegator agent."
    )
    system_message: Optional[str] = Field(
        None, description="System message for the research delegator agent."
    )
    token_budget: int = Field(
        5000, description="Token budget for the research delegator agent."
    )
    minimum_research_topics: int = Field(
        3, description="Minimum number of research topics to generate."
    )
    maximum_research_topics: int = Field(
        5, description="Maximum number of research topics to generate."
    )


class ResearcherConfig(ConfiguredBaseModel):
    language_model_name: str = Field(
        "gpt-4.1", description="The name of the language model used by the researcher agent."
    )
    system_message: Optional[str] = Field(
        None, description="System message for the researcher agent."
    )
    token_budget: int = Field(
        5000, description="Token budget for each researcher."
    )


class ReviewerConfig(ConfiguredBaseModel):
    language_model_name: str = Field(
        "o3-mini", description="The name of the language model used by the reviewer agent."
    )
    system_message: Optional[str] = Field(
        None, description="System message for the reviewer agent."
    )
    token_budget: int = Field(
        5000, description="Token budget for the reviewer agent."
    )
    max_revisions: int = Field(2, description="Maximum number of revisions allowed.")


class RefinerConfig(ConfiguredBaseModel):
    language_model_name: str = Field(
        "gpt-4.1", description="The name of the language model used by the refiner agent."
    )
    system_message: Optional[str] = Field(
        None, description="System message for the refiner agent."
    )
    token_budget: int = Field(
        25000, description="Token budget for the refiner agent."
    )


class DeepResearchConfig(ConfiguredBaseModel):
    enabled: bool = Field(False, description="Whether deep research is enabled.")
    research_delegator: Optional[ResearchDelegatorConfig] = Field(
        ResearchDelegatorConfig(), description="Configuration for the research delegator."
    )
    researcher: Optional[ResearcherConfig] = Field(
        ResearcherConfig(), description="Configuration for the researcher."
    )
    reviewer: Optional[ReviewerConfig] = Field(
        ReviewerConfig(), description="Configuration for the reviewer."
    )
    refiner: Optional[RefinerConfig] = Field(
        RefinerConfig(), description="Configuration for the refiner."
    )
