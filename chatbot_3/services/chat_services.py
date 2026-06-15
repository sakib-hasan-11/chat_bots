from core.model_loader import llm
from core.mysql_loader import MySQLService
from utils.message_builder import build_langchain_messages

from services.long_term_memory_service import LongTermMemoryService
from services.redis_services import (
    initialize_chat,
    load_recent_history,
    load_redis_client,
    save_ai_message_redis,
    save_user_message_redis,
)

memory_service = LongTermMemoryService()
redis_client = load_redis_client()
mysql = MySQLService()


async def generate_response(user_id: str, user_input: str):

    initialize_chat(user_id)

    save_user_message_redis(user_id=user_id, user_query=user_input)

    user_db_id = mysql.create_user_if_not_exists(user_id)

    conversation_id = mysql.get_or_create_active_conversation(user_db_id)

    mysql.save_message(conversation_id, "user", user_input)

    history = load_recent_history(user_id)

    messages = build_langchain_messages(history)

    response = await llm.ainvoke(messages)  # must use ainvoke with await.

    save_ai_message_redis(user_id, response.content)

    redis_client.ltrim(f"chat_{user_id}", -21, -1)

    mysql.save_message(conversation_id, "assistant", response.content)

    await memory_service.update_memory(
        user_id=user_id,
        conversation_id=conversation_id,
    )

    return response.content
