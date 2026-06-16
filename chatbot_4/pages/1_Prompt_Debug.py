import os
import time

import requests
import streamlit as st
from dotenv import load_dotenv

# ---------------------------------------
# Config
# ---------------------------------------

load_dotenv()

API_URL = os.getenv("API_URL")

DEBUG_URL = f"{API_URL}/chat/debug"

st.set_page_config(
    page_title="Prompt Debug",
    layout="wide",
)

st.title("🧠 Prompt Debugger")

refresh = st.sidebar.slider(
    "Auto Refresh (seconds)",
    1,
    10,
    2,
)

placeholder = st.empty()

while True:

    try:

        debug = requests.get(DEBUG_URL).json()

    except Exception:

        placeholder.error("Cannot connect to FastAPI.")

        break

    with placeholder.container():

        st.subheader("Prototype Classifier")

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Similarity Score",
                f"{debug.get('prototype_score',0):.2f}"
            )

        with col2:

            st.metric(
                "Need Memory",
                str(debug.get("need_memory",False))
            )

        st.divider()

        st.subheader("Redis Fact Table")

        st.json(
            debug.get(
                "redis_fact",
                {},
            )
        )

        st.divider()

        st.subheader("Retrieved Pinecone Memories")

        memories = debug.get(
            "retrieved_memories",
            [],
        )

        if memories:

            for memory in memories:

                st.success(memory)

        else:

            st.info("No memories retrieved.")

        st.divider()

        st.subheader("Final Prompt")

        st.code(

            debug.get(
                "final_prompt",
                "No prompt generated yet.",
            ),

            language="text",
        )

    time.sleep(refresh)

    st.rerun()