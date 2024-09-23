from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import (
    RunnableLambda,
    ConfigurableFieldSpec,
    RunnablePassthrough,
)

from pydantic import BaseModel, Field
from typing import List
from environs import Env

env = Env()
env.read_env()

prompt = ChatPromptTemplate.from_messages([
    ("system", """You're an assistant who should only respond to health-related topics such as:
    General health and lifestyle inquiries, Questions about the patient’s medical condition, medication regimen, diet, etc and Requests from the patient to their doctor such as medication changes.
    You should filter out and ignore any unrelated, sensitive, or controversial topics.
    Under any circumstances, only answer related questions using patients's details : {user_info}"""),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}"),
])

# TO-DO: FIX HARD CODED MODEL
chain = prompt | ChatOllama(model = "llama3.1:8b-instruct-fp16",temperature = 0.2)

# TO-DO: SAVE IN THE POSTGRES DATABASE
store = {}

class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    """In memory implementation of chat message history."""

    messages: List[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: List[BaseMessage]) -> None:
        """Add a list of messages to the store"""
        self.messages.extend(messages)

    def clear(self) -> None:
        self.messages = []


def get_session_history(user_id: str, conversation_id: str) -> BaseChatMessageHistory:
    if (user_id, conversation_id) not in store:
        store[(user_id, conversation_id)] = InMemoryHistory()
    return store[(user_id, conversation_id)]

with_message_history = RunnableWithMessageHistory(
    chain,
    get_session_history=get_session_history,
    input_messages_key="question",
    history_messages_key="history",
    history_factory_config=[
        ConfigurableFieldSpec(
            id="user_id",
            annotation=str,
            name="User ID",
            description="Unique identifier for the user.",
            default="",
            is_shared=True,
        ),
        ConfigurableFieldSpec(
            id="conversation_id",
            annotation=str,
            name="Conversation ID",
            description="Unique identifier for the conversation.",
            default="",
            is_shared=True,
        ),
    ],
)

