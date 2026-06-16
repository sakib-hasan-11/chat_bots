from core.model_loader import llm
from core.mysql_loader import MySQLService
from utils.message_builder import build_langchain_messages

from services.long_term_memory_service import LongTermMemoryService
from services.pinecone_service import PineconeService
from services.prototype_classifier import PrototypeClassifier
from services.redis_services import (
    initialize_chat,
    load_fact_memory,
    load_recent_history,
    load_redis_client,
    save_ai_message_redis,
    save_user_message_redis,
)

Pinecone = PineconeService()
prototype_classifier = PrototypeClassifier()

redis_client = load_redis_client()
mysql = MySQLService()
memory_service = LongTermMemoryService(mysql=mysql)
# only for debuging .
last_debug = {}

MEMORY_FIELDS = [
    "career_goals",
    "preferences",
    "skills",
    "projects",
    "current_focus",
]

async def generate_response(user_id: str, user_input: str):

    initialize_chat(user_id)

    save_user_message_redis(user_id=user_id, user_query=user_input)

    user_db_id = mysql.create_user_if_not_exists(user_id)

    conversation_id = mysql.get_or_create_active_conversation(user_db_id)

    print(conversation_id) # for debug

    mysql.save_message(conversation_id, "user", user_input)

    need_memory, score = prototype_classifier.needs_memory(
        user_query=user_input, threshold=0.5
    )

    print(f"memory retrival score from vector db :{score:.3f}")

    if need_memory:
        Pinecone.search_memory(user_id=user_id, query=user_input)

    retrieved_facts = []
    history = load_recent_history(user_id)

    recent_fact_table = load_fact_memory(user_id=user_id)

    messages = build_langchain_messages(
        history, recent_fact_table=recent_fact_table, retrieved_facts=retrieved_facts
    )

    # only for debugging :
    prompt_text = ""

    for msg in messages:
        prompt_text += f"\n\n[{msg.type.upper()}]\n"

        prompt_text += msg.content  # debug code end here .

    response = await llm.ainvoke(messages)  # must use ainvoke with await.

    print(type(messages))
    print(messages)

    save_ai_message_redis(user_id, response.content)

    redis_client.ltrim(f"chat_{user_id}", -21, -1)

    mysql.save_message(conversation_id, "assistant", response.content)

    print('user message saved')

    await memory_service.update_memory(
        user_id=user_id,
        conversation_id=conversation_id,
    
    )
    # only for debugging :
    global last_debug
    last_debug = {
        "prototype_score": score,
        "need_memory": need_memory,
        "redis_fact": recent_fact_table,
        "retrieved_memories": retrieved_facts,
        "final_prompt": prompt_text,
    } # end here .


    return response.content
