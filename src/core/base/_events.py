from src.models.tool import ToolArtifact
from langchain_core.callbacks.manager import dispatch_custom_event
from src.models.intermediate_step import IntermediateStep

class LamBotEvents:
    """Class for dispatching events related to LamBot operations."""

    @staticmethod
    def dispatch_tool_artifact(tool_artifact: ToolArtifact):
        """Dispatches a custom event with the tool artifact.

        Args:
            tool_artifact (ToolArtifact): The tool artifact to dispatch.
        """
        dispatch_custom_event(
            name="tool_artifact",
            data={"artifact": tool_artifact},
        )

    @staticmethod
    def dispatch_intermediate_step(intermediate_step: IntermediateStep):
        """Dispatches a custom event with the intermediate step.

        Args:
            intermediate_step (IntermediateStep): The intermediate step to dispatch.
        """
        dispatch_custom_event(
            name="intermediate_step",
            data={"intermediate": intermediate_step},
        )