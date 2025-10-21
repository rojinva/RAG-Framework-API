import requests
import json
from copy import deepcopy
from typing import List, Dict, Any

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

from langchain_community.chat_models import AzureChatOpenAI
from langchain.tools.retriever import create_retriever_tool
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
    ChatPromptTemplate,
)
from langchain_core.agents import AgentAction

from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.memory import ChatMessageHistory
from src.clients.azure import openai_token_provider

class CustomHandler(BaseCallbackHandler):
    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> Any:
        formatted_prompts = "\n".join(prompts)
        print(f"===== Begin prompt\n{formatted_prompts}\n===== End prompt")

    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        """Run on agent action."""
        print(f"===== Begin agent action\n{action.log}\n===== End agent action")


# # Azure OpenAI config
# openai_api_key = "" # Fill in manually
# openai_api_base = "https://dfapidmdev-gw.lamrc.net/"
# openai_api_version = "2023-03-15-preview"
# deployment_name = "test_gpt_4_32k"

# # Azure OpenAI config
# openai_api_key = "" # Fill in manually
# openai_api_base = "https://oai-lam-use-dfab-dev-eng-001.openai.azure.com/"
# openai_api_version = "2023-03-15-preview"
# deployment_name = "test_gpt_4_32k"

# Azure OpenAI config
openai_api_key = ""  # Fill in manually
openai_api_base = "https://oai-lam-usw-dfab-dev-eng-001.openai.azure.com/"
openai_api_version = "2023-03-15-preview"
deployment_name = "gpt-4o"

# Azure AI Search config
search_api_key = ""  # Fill in manually
search_api_base = "https://srch-lam-usw-oai-dev-eng-02.search.windows.net"
search_api_version = "2024-03-01-preview"
index_name = "index-oai-commonspec"

# Create LLM
llm = AzureChatOpenAI(
    azure_ad_token_provider=openai_token_provider,
    azure_endpoint=openai_api_base,
    api_version=openai_api_version,
    deployment_name=deployment_name,
    temperature=0.0,
    streaming=False,
)


# Wrap LLM to intercept calls
class AzureChatOpenAIClientWrapper:
    def __init__(self, wrapped_class):
        """
        Wrapper class used to inspect actual HTTP request and response sent to Azure OpenAI chat completion.

        Reference: https://github.com/langchain-ai/langchain/discussions/6511
        """
        self.wrapped_class = wrapped_class

    def __getattr__(self, attr):
        original_func = getattr(self.wrapped_class, attr)

        def wrapper(*args, **kwargs):
            print(f"Calling function: {attr}")
            print(f"Arguments: {args}, {kwargs}")
            result = original_func(*args, **kwargs)
            print(f"Response: {result}")
            return result

        return wrapper


llm.client = AzureChatOpenAIClientWrapper(llm.client)


# Define retriever
class AzureAISearchRetriever(BaseRetriever):
    """
    TBD: Re-write this as custom Tool, not implementing BaseRetriever, so that we can write our own
    tool description and add our own tool parameters and tool parameter descriptions.

    LangChain has its own Azure AI Search retriever class, but it makes its own decisions on how to call
    different search types and such. Here, we are using the same model where we provide search query
    REST API kwargs and possibly override the "search" field and "vectorQueries" text field.
    """

    search_params: Dict[str, Any]

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:

        payload = deepcopy(self.search_params)
        url = f"{search_api_base}/indexes/{index_name}/docs/search?api-version={search_api_version}"
        headers = {"Content-Type": "application/json", "api-key": search_api_key}

        # Inject the query into the search params
        # The way to force pure-vector search is to set "search" to None
        if "search" in payload and payload["search"] is not None:
            payload["search"] = query
        if "vectorQueries" in payload:
            payload["vectorQueries"][0]["text"] = query

        # Execute the search
        search_response = requests.post(
            url=url, headers=headers, data=json.dumps(payload)
        )
        search_response = json.loads(search_response.content)["value"]

        # Convert response to List[Document]
        documents = []
        for response in search_response:
            page_content = response.pop("chunk")
            documents.append(
                Document(page_content=page_content, metadata={"row": response["row"]})
            )

        ##### OVERRIDE FAKE CITATIONS
        documents = [
            # Document(page_content="[1] The Lam response to light tower is comply. This response was made on Januray 1, 2020.")
            Document(page_content="[1] The Etch response to light tower is comply."),
            Document(
                page_content="[2] The Dep response to light tower is do not comply."
            ),
        ]

        return documents


# Create retriever
search_params = {"top": 5}
retriever = AzureAISearchRetriever(search_params=search_params)


# Create retriever tool
retriever_tool = create_retriever_tool(
    retriever,
    "search_customer_spec",
    "Searches and returns Lam responses to customer specifications.",
)
tools = [retriever_tool]

# Create messages prompt
prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate(
            prompt=PromptTemplate(
                input_variables=[],
                template="You are a helpful assistant. When citing sources, use brackets like [1].",
            )
        ),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        HumanMessagePromptTemplate(
            prompt=PromptTemplate(input_variables=["input"], template="{input}")
        ),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)


# Create agent
agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, return_intermediate_steps=True)

# Add memory
memory = ChatMessageHistory(session_id="test-session")
agent_with_chat_history = RunnableWithMessageHistory(
    agent_executor,
    # This is needed because in most real world scenarios, a session id is needed
    # It isn't really used here because we are using a simple in memory ChatMessageHistory
    lambda session_id: memory,
    input_messages_key="input",
    history_messages_key="chat_history",
)

invoke_config = {
    "configurable": {"session_id": "<foo>"},
    "callbacks": [CustomHandler()],
}

# First message
result = agent_with_chat_history.invoke({"input": "Hi, I'm Bob."}, config=invoke_config)
print("\n##### 1st message start")
print(result["output"])
print("##### 1st message end\n")

# Second message
result = agent_with_chat_history.invoke(
    {
        "input": "What is the Etch response to light tower? Respond only with the term 'Comply' or 'Do not comply' and the citation in square brackets; nothing else."
    },
    config=invoke_config,
)
print("\n##### 2nd message start")
print(result["output"])
print("##### 2nd message end\n")

# Third message
result = agent_with_chat_history.invoke(
    {"input": "What about the Dep response?"}, config=invoke_config
)
print("\n##### 3rd message start")
print(result["output"])
print("##### 3rd message end\n")

# # Fourth message
# result = agent_with_chat_history.invoke({"input": "Thanks for the help!"},
#                                         config=invoke_config)
# print("\n##### 4th message start")
# print(result["output"])
# print("##### 4th message end\n")
