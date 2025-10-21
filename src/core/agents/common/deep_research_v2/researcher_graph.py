import os
from dotenv import load_dotenv

load_dotenv(override=True)

from langgraph.graph import START, END, StateGraph
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
    ChatPromptTemplate,
)
from langgraph.types import Command, Send
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.runnables import RunnableConfig

from src.core.base import LamBotGraph
from src.models.intermediate_step import IntermediateStep
from src.core.agents.utils import initialize_azure_llm_from_model_name
from src.core.agents.common.deep_research_v2.models import (
    DeepResearchLanggraphConfig,
    ResearcherScratchpad,
    DraftSection,
    Review,
)
from src.core.agents.common.deep_research_v2.prompts import (
    RESEARCHER_SYSTEM_MESSAGE,
    REVIEWER_SYSTEM_MESSAGE,
)
from src.core.agents.common.deep_research_v2.utils import get_deep_research_config

class Researcher(LamBotGraph):
    def __init__(self):

        # Build the graph
        self._graph = self.build_graph()
        self.graph = self._graph.compile()

    def build_graph(self):
        graph = StateGraph(ResearcherScratchpad)
        graph.add_node("researcher", self._researcher)
        graph.add_node("reviewer", self._reviewer)
        graph.add_edge(START, "researcher")
        graph.add_edge("researcher", "reviewer")
        graph.add_edge("reviewer", END)
        return graph
    
    async def _researcher(self, scratchpad: ResearcherScratchpad, config: RunnableConfig):
        config: DeepResearchLanggraphConfig = get_deep_research_config(config)

        self.dispatch_intermediate_step(
            intermediate_step=IntermediateStep(
                message=f"Researcher is generating a draft for the topic '{scratchpad.section.title}'"
            )
        )
        section = scratchpad.section

        if not scratchpad.local_messages:
            scratchpad.local_messages.append(
                HumanMessage(content=section.query)
            )

        researcher_system_message = (
            config.researcher.system_message
            or self._get_prompt(
                prompt_name="RESEARCHER_SYSTEM_MESSAGE",
                fallback_prompt=RESEARCHER_SYSTEM_MESSAGE,
                label=os.getenv("LANGFUSE_LABEL", "dev"),
            )
        )

        system_message_template = SystemMessagePromptTemplate(
            prompt=PromptTemplate(
                input_variables=[],
                template=researcher_system_message,
            )
        )

        chat_history_template = MessagesPlaceholder(
            variable_name="chat_history", optional=True
        ).format_messages(chat_history=scratchpad.local_messages)

        agent_scratchpad_template = MessagesPlaceholder(
            variable_name="agent_scratchpad", optional=True
        )

        # Assemble and return the complete chat prompt template.
        prompt = ChatPromptTemplate.from_messages(
            [system_message_template]
            + chat_history_template
            + [agent_scratchpad_template]
        )

        # Initialize the model
        llm = initialize_azure_llm_from_model_name(
            config.researcher.language_model_name, tags=["researcher"], streaming=False, max_completion_tokens=config.researcher.token_budget
        )

        _agent = create_tool_calling_agent(
            llm=llm,
            tools=config.tools,
            prompt=prompt,
        )

        agent = AgentExecutor(
            name="Researcher",
            agent=_agent,
            tools=config.tools,
            verbose=False,
            return_intermediate_steps=True,
            handle_parsing_errors=True,
        )

        section_draft_generated_by_agent = await agent.ainvoke({"messages": prompt})

        scratchpad.local_messages.append(
            AIMessage(content=section_draft_generated_by_agent["output"])
        )

        scratchpad.draft = DraftSection(
            title=section.title,
            content=section_draft_generated_by_agent["output"],
        )
        return scratchpad

    async def _reviewer(self, scratchpad: ResearcherScratchpad, config: RunnableConfig):
        self.dispatch_intermediate_step(
            intermediate_step=IntermediateStep(
                message=f"Reviewer is evaluating the draft for the topic '{scratchpad.section.title}'"
            )
        )
        section = scratchpad.section
        title = section.title
        draft = scratchpad.draft
        acceptance_criteria = section.acceptance_criteria

        config: DeepResearchLanggraphConfig = get_deep_research_config(config)

        # Initialize the model
        llm = initialize_azure_llm_from_model_name(
            config.reviewer.language_model_name, tags=["reviewer"], streaming=False, max_completion_tokens=config.reviewer.token_budget
        )

        llm_with_structured_output = llm.with_structured_output(schema=Review)

        reviewer_system_message = (
            config.reviewer.system_message
            or self._get_prompt(
                prompt_name="REVIEWER_SYSTEM_MESSAGE",
                fallback_prompt=REVIEWER_SYSTEM_MESSAGE,
                label=os.getenv("LANGFUSE_LABEL", "dev"),
            )
        )

        messages = [
            SystemMessage(content=f"{reviewer_system_message} \n\n Acceptance Criteria\n{acceptance_criteria}")
        ] + scratchpad.local_messages

        review: Review = await llm_with_structured_output.ainvoke(
            input=messages
        )

        scratchpad.local_messages.append(
            HumanMessage(content=review.feedback)
        )

        if review.passed:
            self.dispatch_intermediate_step(
                intermediate_step=IntermediateStep(
                    message=f"Draft for the topic '{title}' has been approved..."
                )
            )

            scratchpad.local_messages.append(
                HumanMessage(content=f"Great job! The draft for the topic '{title}' has been completed.")
            )
            return {"draft_sections": [draft]}
        
        # Check if the revision count has reached the maximum allowed revisions
        if scratchpad.revision_count >= config.reviewer.max_revisions:
            self.dispatch_intermediate_step(
                intermediate_step=IntermediateStep(
                    message=f"Maximum revisions reached for the topic '{title}'. Returning the last draft..."
                )
            )
            return {"draft_sections": [draft]}

        # Increment the revision count and loop back to the researcher
        scratchpad.revision_count += 1

        self.dispatch_intermediate_step(
            intermediate_step=IntermediateStep(
                message=f"Draft for the topic '{title}' did not meet the acceptance criteria. Circling back to the researcher for revisions (Revision {scratchpad.revision_count}/{config.reviewer.max_revisions})..."
            )
        )

        return Command(
            goto=[
                Send(
                    "researcher",
                    ResearcherScratchpad(
                        section=section,
                        draft=draft,
                        local_messages=scratchpad.local_messages,
                        revision_count=scratchpad.revision_count,
                    ),
                )
            ],
        )
