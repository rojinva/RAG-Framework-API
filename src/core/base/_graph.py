from src.core.base import LamBotEvents
from src.core.base.utils import get_prompt

class LamBotGraph(LamBotEvents):
    """LamBotGraph class inheriting shared functionality from LamBotEvents."""

    def build_graph(self):
        """Build the graph."""
        raise NotImplementedError("Subclasses should implement this method.")
    
    @staticmethod
    def _get_prompt(prompt_name: str, fallback_prompt: str, label: str) -> str:
        """Fetches a prompt from LangfuseManager or uses a fallback prompt.

        Args:
            prompt_name (str): The name of the prompt to fetch.
            fallback_prompt (str): The fallback prompt to use if the prompt is not found.
            label (str): The label for the prompt.

        Returns:
            str: The fetched prompt.
        """
        return get_prompt(prompt_name, fallback_prompt, label)