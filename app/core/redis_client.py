#建立 Redis 連線（client）→ 其他地方用 get_redis() 拿 --》 和 database.py 原理一樣

import redis.asyncio as aioredis
from iris.config import settings

_client: aioredis.Redis | None = None


def get_redis() -> aioredis.Redis:
    global _client
    if _client is None:
        _client = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _client