import os

import requests
import streamlit as st
from dotenv import load_dotenv
from services.redis_services import (
    initialize_chat,
    load_history,
    load_redis_client,
    save_ai_message_redis,
    save_user_message_redis,
)

# -----------------------------------
# Config
# -----------------------------------

load_dotenv()

API_URL = os.getenv("API_URL")

st.set_page_config(page_title="Chatbot", layout="centered")

redis_client = load_redis_client()

user_id = "user_123"

initialize_chat(user_id)

# -----------------------------------
# Load history ONLY ONCE
# -----------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = load_history(user_id=user_id, limit=20)

# -----------------------------------
# Display chat
# -----------------------------------

for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue

    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# -----------------------------------
# Chat Input
# -----------------------------------

user_input = st.chat_input("Type your message...")


if user_input:
    # ---------------------------
    # Show user instantly
    # ---------------------------

    user_message = {"role": "user", "content": user_input}

    st.session_state.messages.append(user_message)

    with st.chat_message("user"):
        st.write(user_input)

    save_user_message_redis(user_id=user_id, user_query=user_input)

    # ---------------------------
    # Assistant
    # ---------------------------

    payload = {"user_id": user_id, "message": user_input}

    with st.chat_message("assistant"):
        placeholder = st.empty()

        placeholder.markdown("Thinking...**")

        response = requests.post(API_URL, json=payload)

        assistant_reply = response.json()["response"]

        placeholder.empty()

        st.write(assistant_reply)

    assistant_message = {"role": "assistant", "content": assistant_reply}

    st.session_state.messages.append(assistant_message)

    save_ai_message_redis(user_id=user_id, ai_response=assistant_reply)

    redis_client.ltrim(f"chat_{user_id}", -21, -1)
