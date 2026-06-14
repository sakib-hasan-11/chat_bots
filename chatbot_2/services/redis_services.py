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


def save_ai_message_redis(user_id: str, ai_response: str):
    key = f"chat_{user_id}"

    redis_client.rpush(key, json.dumps({"role": "assistant", "content": ai_response}))
