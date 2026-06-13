import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage,HumanMessage,AIMessage
from dotenv import load_dotenv
import os
load_dotenv()


def load_chat_model():
    model=ChatOpenAI(
        model='gpt-4o-mini',
        api_key=os.getenv('OPENAI_API_KEY'),
        temperature=1
    )

    return model

def create_message_prompt(user_input):
    message = [
        SystemMessage(content='you are a 5 years experienced senior ml engineer'),
        HumanMessage(content=user_input)
    ]

    return message


model = load_chat_model()

st.title("lang chain practise day - 1 ")

prompt = st.chat_input(placeholder="message here")



if prompt :

    message=create_message_prompt(prompt)

    with st.chat_message(name="user"):
        
        st.write(prompt)
    
    with st.chat_message(name="assistant"):
        responce = model.invoke(message)

        st.write(responce.content)
        





