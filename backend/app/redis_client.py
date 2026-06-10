import os
import redis
from dotenv import load_dotenv

load_dotenv()

_client: redis.Redis | None = None


def get_redis() -> redis.Redis | None:
    global _client
    if _client is not None:
        return _client
    try:
        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", 6379))
        _client = redis.Redis(host=host, port=port, decode_responses=True, socket_connect_timeout=2)
        _client.ping()
        return _client
    except Exception:
        _client = None
        return None
