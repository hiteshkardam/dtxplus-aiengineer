from langchain_ollama import ChatOllama
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, FewShotChatMessagePromptTemplate
from langchain_postgres import PostgresChatMessageHistory
from langchain_core.runnables import (
    RunnableLambda,
    ConfigurableFieldSpec,
    RunnablePassthrough,
)

from pydantic import BaseModel, Field
from typing import List
from environs import Env
import os
import psycopg

env = Env()
env.read_env()

os.environ["LANGCHAIN_TRACING_V2"]=env.str('LANGCHAIN_TRACING_V2')
os.environ["LANGCHAIN_API_KEY"]=env.str('LANGCHAIN_API_KEY')
os.environ["LANGCHAIN_ENDPOINT"]=env.str('LANGCHAIN_ENDPOINT')
os.environ["LANGCHAIN_PROJECT"]=env.str('LANGCHAIN_PROJECT')

examples = [
    {"input": "Can we reschedule the appointment?", "output": "At what date and time would you like to reshedule?"},
    {"input": "Can we reschedule the appointment to next Friday at 3 PM", "output": "I will convey your request to Dr. [Doctor's Name]."},
]

example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}"),
    ]
)

few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=example_prompt,
    examples=examples,
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You're a doctor's assistant helping patients with their information and should only respond health-related topics such as:\n\
    General health and lifestyle inquiries, Questions about the patient’s medical condition, medication regimen, diet, etc and Requests from the patient to their doctor such as medication changes and rescheduling.\n\
    You should filter out and ignore any unrelated, sensitive, or controversial topics.\n\
    Patients's details : {user_info}"),
    "Use this conversation as examples of how to respond:",
    few_shot_prompt,
    "This is our previos conversation:",
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}"),
])

# TO-DO: FIX HARD CODED MODEL
chain = prompt | ChatOllama(model = "llama3.1:8b-instruct-fp16",temperature = 1.0)

conn_info = "postgresql://test:f00b%40rdtxp@localhost/dtxplus"
sync_connection = psycopg.connect(conn_info)
table_name = "message_store"

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    print(f"{session_id=} {type(session_id)=}")
    return PostgresChatMessageHistory(
        table_name,
        session_id,
        sync_connection=sync_connection
)

with_message_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="question",
    history_messages_key="history",
)