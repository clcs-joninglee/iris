#refresh token 的核心邏輯
#refresh token 長這樣：abc123.xyz789randomsecret，前面是 token_id，後面是 token_secret，用 . 分開。

import hashlib
import secrets
from datetime import timedelta

from iris.config import settings
from app.core.redis_client import get_redis

_TTL = int(timedelta(days=settings.refresh_token_ttl_days).total_seconds())
_TOMBSTONE_TTL = 60 * 60 * 24  # 24 小時，記錄已 rotate 的 token


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest() #把 token_secret 用 sha256 雜湊後存到 Redis，這樣即使 Redis 被攻破，攻擊者也拿不到真正的 token_secret


async def create_refresh_token(user_id: int) -> str: #創建 refresh token，存到 Redis，回傳給 client
    token_id = secrets.token_urlsafe(8) #當作key的一部分（識別這個token）
    token_secret = secrets.token_urlsafe(32) #真正的秘密，雜湊後存redis
    redis = get_redis()
    await redis.set(f"refresh:{user_id}:{token_id}", _hash(token_secret), ex=_TTL)
    return f"{token_id}.{token_secret}"


async def verify_refresh_token(token: str) -> int | None: #驗證 refresh token，從 Redis 找對應的 key，拿到雜湊後的秘密，比對是否正確，回傳 user_id 或 None
    try:
        token_id, token_secret = token.split(".", 1)
    except ValueError:
        return None
    redis = get_redis()

    # B1：檢查是否是已 rotate 的舊 token
    tombstone = await redis.get(f"refresh_used:{token_id}")
    if tombstone:
        # 有人重用舊 token，撤銷該 user 全部 session
        await revoke_all_refresh_tokens(int(tombstone))
        return None

    async for key in redis.scan_iter(f"refresh:*:{token_id}"):
        stored = await redis.get(key)
        if stored == _hash(token_secret):
            return int(key.split(":")[1])
    return None



async def revoke_refresh_token(token: str) -> None: #撤銷 refresh token，從 Redis 找到對應的 key 刪除，這樣這個 token 就不能再用了
    try:
        token_id, _ = token.split(".", 1)
    except ValueError:
        return
    redis = get_redis()
    async for key in redis.scan_iter(f"refresh:*:{token_id}"):
        user_id = key.split(":")[1]
        await redis.delete(key)
        # 留下 tombstone，讓 reuse detection 能偵測到
        await redis.set(f"refresh_used:{token_id}", user_id, ex=_TOMBSTONE_TTL)


async def revoke_all_refresh_tokens(user_id: int) -> None: #撤銷某個 user 的所有 refresh token，從 Redis 找到對應的 key 刪除，這樣這個 user 的所有 refresh token 都不能再用了（例如改密碼後）
    redis = get_redis()
    async for key in redis.scan_iter(f"refresh:{user_id}:*"):
        await redis.delete(key)