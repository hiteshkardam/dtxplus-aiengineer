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
    {"input": "Can we reschedule the appointment?", "output": "At what date and time would you like to reschedule?"},
    {"input": "Can we reschedule the appointment to next Friday at 3 PM?", "output": "I will convey your request to Dr. [Doctor's Name]."},
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
    ("system",
    "You are an intelligent assistant acting as a doctor's medical assistant. Your primary role is to assist patients with administrative tasks and forward requests to the doctor. \
    You **must not** take any direct actions (such as rescheduling appointments or providing medical advice) on behalf of the doctor. Instead, you should always forward these requests to the doctor.\n\n\
    Your scope includes:\n\
    - General health and lifestyle inquiries (without giving medical advice)\n\
    - Forwarding patient requests to the doctor (e.g., medication changes, appointment rescheduling, missed doses)\n\n\
    For all requests, you should politely inform the patient that you will pass their request on to the doctor for further action. Never make decisions or perform tasks on your own.\n\
    If a request falls outside of health-related inquiries or administrative tasks, kindly decline to respond and inform the patient that the request is outside your scope.\n\
    The patient details are\n{user_info}"),
    ("system", "Please follow this example behavior:"),#\n{few_shot_prompt}"),
    few_shot_prompt,
    ("system", "The provided chat history includes facts about the patient you are speaking with.",),
    ("placeholder", "{chat_history}"),
    ("human", "{question}"),
])


# TO-DO: FIX HARD CODED MODEL
chain = prompt | ChatOllama(model = "llama3.1:8b-instruct-fp16",temperature = 0.2)

conn_info = "postgresql://test:f00b%40rdtxp@localhost/dtxplus"
sync_connection = psycopg.connect(conn_info)
table_name = "message_store"

# def get_session_history(session_id: str) -> BaseChatMessageHistory:
#     print(f"{session_id=} {type(session_id)=}")
#     return PostgresChatMessageHistory(
#         table_name,
#         session_id,
#         sync_connection=sync_connection
# )

# with_message_history = RunnableWithMessageHistory(
#     chain,
#     get_session_history,
#     input_messages_key="question",
#     history_messages_key="history",
# )

def summarize_messages(session_id: str) -> str:
    # Retrieve the stored messages from Postgres
    stored_messages = PostgresChatMessageHistory(
        table_name,
        session_id,
        sync_connection=sync_connection
    ).messages
    
    # print(f"{len(stored_messages)=}")

    # If no messages are found, return an empty string (no summary)
    if len(stored_messages) == 0:
        return ""

    # Summarization prompt for distilling chat messages
    summarization_prompt = ChatPromptTemplate.from_messages(
        [
            ("placeholder", "{chat_history}"),
            (
                "user",
                "Distill the chat history into a concise summary.\
                Include as many specific details as possible.\
                I am the patient who is asking for this summary.\
                Do not reply with anything other than the summary, no opening or closing statement."
            ),
        ]
    )
    
    # Define the summarization chain using your model
    summarization_chain = summarization_prompt | ChatOllama(
        model="llama3.1:8b-instruct-fp16",
        temperature=0
    )
    
    # Generate the summary using the summarization chain
    summary_message = summarization_chain.invoke({"chat_history": stored_messages})
    
    # print(f"{summary_message=}")
    # Return the generated summary
    return summary_message

def get_summarized_session_history(session_id: str) -> BaseChatMessageHistory:
    print(f"{session_id=} {type(session_id)=}")
    
    # Summarize the history
    summary = summarize_messages(session_id)
    
    # Create a new message history object, with the summary as the only message
    summarized_history = PostgresChatMessageHistory(
        table_name,
        session_id,
        sync_connection=sync_connection
    )
    
    # Clear the existing history and replace it with the summary
    # summarized_history.clear()
    # summarized_history.add_message(summary)

    return summarized_history

# Pass the summarized history instead of the entire history
with_summarized_history = RunnableWithMessageHistory(
    chain,
    get_summarized_session_history,
    input_messages_key="question",
    history_messages_key="chat_history"
)
