import json
import os

import redis
import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

load_dotenv()

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)


@st.cache_resource
def load_model():
    model = ChatOpenAI(
        name="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"), temperature=1
    )
    return model


def create_prompt(user_input):
    message = [
        SystemMessage(content="you are a senior experienced ml engineer"),
        HumanMessage(content=user_input),
    ]

    return message


# initial with user id and save system message of once only .
def initalize_chat(user_id: str = "user_123"):

    key = f"chat:{user_id}"  # separated user key to store the chats

    if redis_client.exists(key):  # if key already in redis do nothing
        return

    else:  # if not key saved then store it with the system message for once.
        system_message = {  # python dict
            "role": "system",
            "content": "you are a senior experienced ml engineer",
        }

        redis_client.rpush(  # rpush acts like append in redis. it need key value pair to store .
            # rpush create a list and keep the key value in the list like :['{"role":"system","content":"You are an ML engineer"}',]
            key,  # user id as the key
            json.dumps(system_message),  # resis cant store dict so convert it into json
            # system message as the value
        )


def load_histry_redis(user_id: str = "user_123", limit=20):
    key = f"chat:{user_id}"  # 1st load the key

    message = redis_client.lrange(
        key, -limit, -1
    )  # lrange(list range) work like a python range to fetch all the message of the user chat
    # lrange(key,0,-1) : lrange(key,start,stop)

    return [
        json.loads(el) for el in message
    ]  # return all the message of a user in a nested list format .


# [
#  '{"role":"system","content":"You are an ML engineer"}',

#  '{"role":"user","content":"Hello"}',

#  '{"role":"assistant","content":"Hi there"}'
# ]


# convert redis histry chat into langchain message
def build_langchain_message(user_id: str = "user_123"):

    histry = load_histry_redis(user_id=user_id)

    if len(histry) == 0:
        return []

    message = []

    for el in histry:
        if el["role"] == "system":
            message.append(SystemMessage(content=el["content"]))
        elif el["role"] == "user":
            message.append(HumanMessage(content=el["content"]))
        elif el["role"] == "assistant":
            message.append(AIMessage(content=el["content"]))

    return message


def save_new_user_message(content: str, user_id: str = "user_123"):
    redis_client.rpush(
        f"chat:{user_id}", json.dumps({"role": "user", "content": content})
    )


def save_new_ai_message(content: str, user_id: str = "user_123"):
    redis_client.rpush(
        f"chat:{user_id}", json.dumps({"role": "assistant", "content": content})
    )


user_id = "user_123"

model = load_model()

st.set_page_config(page_title="chat bot", layout="wide")
st.title("chatbot with memory support")
st.write("---")




initalize_chat(user_id=user_id)
histry = load_histry_redis(user_id=user_id, limit=20)

if len(histry) != 0:
    for msg in histry:
        if msg["role"] == "system":
            continue

        with st.chat_message("user" if msg["role"] == "user" else "assistant"):
            st.write(msg["content"])
user_input = st.chat_input(placeholder="user input")

if user_input:
    # model_prompt = create_prompt(user_input=user_input)

    save_new_user_message(user_id=user_id, content=user_input)

    message = build_langchain_message(user_id=user_id)

    with st.chat_message(name="user"):
        st.write(user_input)

    with st.chat_message(name="assistant"):
        response = model.invoke(message)
        st.write(response.content)

        save_new_ai_message(content=response.content, user_id=user_id)

        redis_client.ltrim(f"chat:{user_id}", -21, -1)
