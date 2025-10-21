import os
from dotenv import load_dotenv

load_dotenv(override=True)

from langgraph.types import Send
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, AIMessage
from langgraph.graph import START, END, StateGraph, MessagesState

from src.core.base import LamBotGraph
from src.models.intermediate_step import IntermediateStep
from src.core.agents.utils import initialize_azure_llm_from_model_name
from src.core.agents.common.deep_research_v2.utils import get_deep_research_config
from src.core.agents.common.deep_research_v2.researcher_graph import Researcher
from src.core.agents.common.deep_research_v2.models import (
    Research,
    FinalAnswer,
    ResearchPlan,
    DeepResearchLanggraphConfig,
)
from src.core.agents.common.deep_research_v2.prompts import (
    RESEARCH_DELEGATOR_SYSTEM_MESSAGE,
    REFINER_SYSTEM_MESSAGE,
)

class DeepResearchAgentV2(LamBotGraph):
    def __init__(self):

        # Build the graph
        self._graph = self.build_graph()
        self.graph = self._graph.compile()

    def build_graph(self):
        graph = StateGraph(
            state_schema=Research,
            config_schema=DeepResearchLanggraphConfig,
            input=MessagesState,
            output=FinalAnswer,
        )
        researcher_graph = Researcher().graph

        graph.add_node("research_delegator", self._research_delegator)
        graph.add_node("researcher", researcher_graph)
        graph.add_node("refiner", self._refiner)

        graph.add_edge(START, "research_delegator")

        graph.add_conditional_edges("research_delegator", self._spawn_researchers)

        graph.add_edge("researcher", "refiner")
        graph.add_edge("refiner", END)

        return graph

    def _research_delegator(self, state: Research, config: RunnableConfig) -> Research:
        self.dispatch_intermediate_step(
            intermediate_step=IntermediateStep(
                message="Research plan is being created. Please wait..."
            )
        )
        messages = state["messages"]

        config: DeepResearchLanggraphConfig = get_deep_research_config(config)

        llm = initialize_azure_llm_from_model_name(
            config.research_delegator.language_model_name,
            tags=["research-delegator"],
            streaming=False,
            max_completion_tokens=config.research_delegator.token_budget
        )

        min_research_topic = config.research_delegator.minimum_research_topics
        max_research_topic = config.research_delegator.maximum_research_topics

        ResearchPlan.configure_length(
            min_length=min_research_topic, max_length=max_research_topic
        )

        llm_with_structured_output = llm.with_structured_output(schema=ResearchPlan)

        research_delegator_system_message = (
            config.research_delegator.system_message
            or self._get_prompt(
                prompt_name="RESEARCH_DELEGATOR_SYSTEM_MESSAGE",
                fallback_prompt=RESEARCH_DELEGATOR_SYSTEM_MESSAGE,
                label=os.getenv("LANGFUSE_LABEL", "dev"),
            )
        )

        system_messages = [
            SystemMessage(content=research_delegator_system_message),
            SystemMessage(content=f"Please ensure that the number of research topics falls within the allowed range of {min_research_topic} to {max_research_topic}.")
        ]

        research_plan: ResearchPlan = llm_with_structured_output.invoke(
            input=system_messages + messages
        )

        state["plan"] = research_plan

        self.dispatch_intermediate_step(
            intermediate_step=IntermediateStep(
                message=f"Research plan created with {len(research_plan.sections)} research tasks..."
            )
        )

        return state

    def _spawn_researchers(self, state: Research, config: RunnableConfig):
        """Spawn researchers for each section in the research plan."""

        self.dispatch_intermediate_step(
            intermediate_step=IntermediateStep(
                message="Delegating research tasks to researchers..."
            )
        )

        return [
            Send("researcher", {"section": s, "local_messages": []})
            for s in state["plan"].sections
        ]

    async def _refiner(self, state: Research, config: RunnableConfig):
        self.dispatch_intermediate_step(
            intermediate_step=IntermediateStep(
                message="Research is now complete. Refining the final answer..."
            )
        )

        messages = state["messages"]
        config: DeepResearchLanggraphConfig = get_deep_research_config(config)

        llm = initialize_azure_llm_from_model_name(
            config.refiner.language_model_name, tags=["lambot-agent-llm"], streaming=True, max_completion_tokens=config.refiner.token_budget
        )

        draft_sections = state["draft_sections"]

        refiner_system_message = (
            config.refiner.system_message
            or self._get_prompt(
                prompt_name="REFINER_SYSTEM_MESSAGE",
                fallback_prompt=REFINER_SYSTEM_MESSAGE,
                label=os.getenv("LANGFUSE_LABEL", "dev"),
            )
        )

        system_message = [SystemMessage(content=refiner_system_message)]
        accumulated_research = [AIMessage(content="\n\n\n\n".join([draft.content for draft in draft_sections]))]

        return {
            "final_answer": await llm.ainvoke(
                input=system_message + messages + accumulated_research
            ),
        }
