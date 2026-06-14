from core.model_loader import llm
from utils.message_builder import build_langchain_messages

from services.redis_services import (
    initialize_chat,
    load_recent_history
)


async def generate_response(user_id: str, user_input: str):

    initialize_chat(user_id)

    history = load_recent_history(user_id)

    messages = build_langchain_messages(history)

    response = await llm.ainvoke(messages) # must use ainvoke with await. 


    return response.content
