import json

import redis


def load_redis_client():
    return redis.Redis(host="localhost", port=6379, decode_responses=True)


redis_client = load_redis_client()


def initialize_chat(user_id: str):
    key = f"chat_{user_id}"

    if redis_client.exists(key):
        return

    redis_client.rpush(
        key,
        json.dumps(
            {
                "role": "system",
                "content": "you are a senior mlops engineer. keep your reply short and concise",
            }
        ),
    )


def load_history(user_id: str, limit=20):
    key = f"chat_{user_id}"

    message = redis_client.lrange(key, -limit, -1)

    return [json.loads(el) for el in message]


def load_recent_history(user_id: str, limit=6):
    key = f"chat_{user_id}"
    message = redis_client.lrange(key, -limit, -1)
    return [json.loads(el) for el in message]


def save_user_message_redis(user_id: str, user_query: str):
    key = f"chat_{user_id}"
    redis_client.rpush(key, json.dumps({"role": "user", "content": user_query}))


# lpush : older to latest order to save .
# rpush : latest to oldest order to save message .
def save_ai_message_redis(user_id: str, ai_response: str):
    key = f"chat_{user_id}"

    redis_client.rpush(
        key, json.dumps({"role": "assistant", "content": ai_response})
    )  # using rpush as number of message will alwys increse.


def save_fact_memory(user_id: str, fact_memory: dict):
    key = f"memory_{user_id}"

    redis_client.set(
        key, json.dumps(fact_memory)
    )  # using set as this fact memory is consitantly same.only one fact memory per user.


def load_fact_memory(user_id: str):

    key = f"memory_{user_id}"

    fact_memory = redis_client.get(key)

    if fact_memory is None:
        return {}  # for new user with no facts we will return null dict. later we will append new facts here .

    return json.loads(fact_memory)


def delete_fact_memory(user_id: str):

    key = f"memory_{user_id}"

    redis_client.delete(key)
