import os

import chainlit as cl

from query import chat_response,read_sql


@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("history", [])
    await cl.Message(
        content="Hello, kindly write your queries related to electoral bond."
    ).send()


@cl.on_message
async def factory(message: str):
    question = message.content
    response = chat_response(question)
    query="SELECT SUM(denominations) FROM bonds_encashed_by_political_parties WHERE date_of_encashment = '2024-04-15' AND political_party_name = 'ALL INDIA ANNA DRAVIDA MUNNETRA KAZHAGAM';"
    read_sql(query)
    await cl.Message(content=response).send()
