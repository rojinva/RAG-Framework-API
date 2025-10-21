from langchain_core.runnables import RunnableConfig
from src.core.agents.common.deep_research_v2.models import (
    DeepResearchLanggraphConfig,
)


def get_deep_research_config(
    run_config: RunnableConfig,
) -> DeepResearchLanggraphConfig:
    """
    Extract & cast the user-supplied configuration block
    from the generic RunnableConfig dict.
    """
    return DeepResearchLanggraphConfig(**run_config["configurable"])
