import os

import requests
import streamlit as st
from dotenv import load_dotenv
from services.redis_services import (
    initialize_chat,
    load_history,
    load_redis_client,
    save_ai_message,
    save_user_message,
)

redis_client = load_redis_client()
load_dotenv()
API_URL = os.getenv("API_URL")


st.set_page_config(page_title="chatbot", layout="centered")

user_id = "user_123"


initialize_chat(user_id)


# load past 20 chat
histry = load_history(user_id=user_id, limit=20)

if len(histry) != 0:
    for msg in histry:
        if msg["role"] == "system":
            continue

        elif msg["role"] == "user":
            with st.chat_message("user"):
                st.write(msg["content"])

        elif msg["role"] == "assistant":
            with st.chat_message("assistant"):
                st.write(msg["content"])


user_input = st.chat_input(placeholder="user input")

if user_input:
    with st.chat_message(name="user"):
        st.write(user_input)
        save_user_message(user_id=user_id, user_query=user_input)

    # this template match the api endpoint input validation schema .
    payload = {"user_id": user_id, "message": user_input}

    with st.chat_message(name="assistant"):
        with st.spinner("thinking... "):
            response = requests.post(url=API_URL, json=payload)
            assistant_reply = response.json()["response"]
        st.write(assistant_reply)
    save_ai_message(ai_response=assistant_reply, user_id=user_id)

    redis_client.ltrim(f"chat_{user_id}", -21, -1)


# uvicorn main:app --reload
# streamlit run app.py
