from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


def build_langchain_messages(history):

    messages = []

    for msg in history:
        if msg["role"] == "system":
            messages.append(SystemMessage(content=msg["content"]))

        elif msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))

        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))

    return messages
