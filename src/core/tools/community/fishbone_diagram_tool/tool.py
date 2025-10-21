import os
import asyncio
from pydantic import BaseModel, Field
from typing import List, Optional, Type, Dict

from src.core.base import LamBotTool
from src.core.tools.community.fishbone_diagram_tool.utils import (
    create_fishbone_diagram,
    format_image_for_chat,
)
from src.models import ToolType
from src.models.intermediate_step import IntermediateStep
from src.models.tool import ToolArtifact
from src.models.constants import MimeType
from src.core.tools.community.fishbone_diagram_tool.prompts import (
    FISHBONE_DIAGRAM_TOOL_DESCRIPTION_PROMPT,
)

from dotenv import load_dotenv
import logging

load_dotenv(override=True)

logger = logging.getLogger(__name__)


class FishboneToolArgsSchema(BaseModel):
    """
    Input schema for the Fishbone tool.
    """

    categories: Optional[Dict[str, List[str]]] = Field(
        ...,
        description="Dictionary for inputs to create fishbone diagram. Keys are categories (like 'People', 'Equipment') and values are lists of specific causes in each category (like ['Lack of training', 'Poor communication']). Try to limit each cause to 50 characters.",
    )


class FishboneDiagramTool(LamBotTool):
    args_schema: Type[BaseModel] = FishboneToolArgsSchema

    def __init__(self):
        super().__init__(
            name="fishbone_diagram_tool",
            description=self._get_prompt(
                prompt_name="FISHBONE_DIAGRAM_TOOL_DESCRIPTION_PROMPT",
                fallback_prompt=FISHBONE_DIAGRAM_TOOL_DESCRIPTION_PROMPT,
                label=os.getenv("LANGFUSE_LABEL", "dev"),
            ),
            tool_type=ToolType.non_retriever_tool,
        )

    async def _execute(self, **kwargs) -> str:
        """
        Shared logic for both sync and async calls.
        """

        try:
            self.dispatch_intermediate_step(
                intermediate_step=IntermediateStep(
                    message="Creating Fishbone diagram...."
                )
            )
            # Try using args schema
            tool_input = self.args_schema(**kwargs)
            # logger.info(f"Fishbone tool input: {tool_input}")
            input_data = tool_input.categories
            logger.info(f"Fishbone tool input data: {input_data}")
            # Create the fishbone diagram
            img_bytes = create_fishbone_diagram(categories=input_data)
            self.dispatch_intermediate_step(
                intermediate_step=IntermediateStep(
                    message="Almost there. Making some final adjustments...."
                )
            )
            markdown_image = format_image_for_chat(img_bytes)

            # Dispatch as tool artifact
            artifact = ToolArtifact(
                content=markdown_image,
                display_name="Fishbone Diagram",
                tool_name=self.name,
                content_type=MimeType.PNG,
            )
            self.dispatch_intermediate_step(
                intermediate_step=IntermediateStep(message="Created fishbone diagram....")
            )
            self.dispatch_tool_artifact(tool_artifact=artifact)
        except Exception as e:
            logger.error(f"Error in FishboneDiagramTool: {e}")
            return f"There was an error when trying to create fishbone diagram: {e}"
        return (
            "A fishbone diagram was created and dispatched to the app. Do not create an image"
        )

    def _run(self, **kwargs) -> str:
        return asyncio.run(self._execute(**kwargs))

    async def _arun(self, **kwargs) -> str:
        return await self._execute(**kwargs)
