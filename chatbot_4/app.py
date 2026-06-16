import os

import requests
import streamlit as st
from dotenv import load_dotenv

# ----------------------------------
# Config
# ----------------------------------

load_dotenv()

user_id = "test_user"

API_URL = os.getenv("API_URL")

CHAT_URL = f"{API_URL}/chat/message"
HISTORY_URL = f"{API_URL}/chat/history/{user_id}"


st.set_page_config(
    page_title="AI Memory Chatbot",
    layout="centered",
)

st.title("AGENTIC CHATBOT WITH LONG CONTEXT MEMORY")

# ----------------------------------
# Session State
# ----------------------------------

history = requests.get(HISTORY_URL).json()

if "messages" not in st.session_state:
    st.session_state.messages = history

if "debug" not in st.session_state:
    st.session_state.debug = {}

# ----------------------------------
# Chat History
# ----------------------------------

for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue

    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ----------------------------------
# Chat Input
# ----------------------------------

user_input = st.chat_input("Type your message...")

if user_input:
    # Show user instantly

    user_message = {
        "role": "user",
        "content": user_input,
    }

    st.session_state.messages.append(user_message)

    with st.chat_message("user"):
        st.write(user_input)

    payload = {
        "user_id": user_id,
        "message": user_input,
    }

    with st.chat_message("assistant"):
        placeholder = st.empty()

        placeholder.markdown("⏳ Thinking...")

        response = requests.post(
            CHAT_URL,
            json=payload,
        )

        data = response.json()

        assistant_reply = data["response"]

        # Save debug information
        st.session_state.debug = data.get("debug", {})

        placeholder.empty()

        st.write(assistant_reply)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": assistant_reply,
        }
    )

    st.rerun()
# uvicorn main:app --reload
# streamlit run app.py
