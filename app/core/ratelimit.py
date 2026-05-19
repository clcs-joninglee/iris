#redis rate limit的邏輯
#兩個功能：1.登入失敗 5 次鎖 15 分鐘 2.同 IP 每分鐘最多 30 次

from app.core.redis_client import get_redis
from iris.config import settings


async def check_login_locked(username: str) -> bool: #檢查登入失敗，以及有沒有失敗超過5次，有就鎖定15分鐘
    redis = get_redis()
    key = f"login_fail:{username}"
    count = await redis.get(key)
    return int(count) >= settings.login_max_failures if count else False


async def record_login_failure(username: str) -> None: #登入失敗後記錄，增加失敗次數，並設定過期時間（鎖定時間）
    redis = get_redis()
    key = f"login_fail:{username}"
    await redis.incr(key)
    await redis.expire(key, settings.login_lockout_minutes * 60)


async def clear_login_failures(username: str) -> None: #登入成功後清除失敗記錄，這樣就不會被鎖定了
    redis = get_redis()
    await redis.delete(f"login_fail:{username}")


async def check_ip_rate_limit(ip: str) -> bool: #檢查同 IP 每分鐘的請求次數，有沒有超過 30 次，如果超過就回傳 True，表示需要限制
    redis = get_redis()
    from datetime import datetime
    minute = datetime.utcnow().strftime("%Y%m%d%H%M")
    key = f"ratelimit:login:ip:{ip}:{minute}"
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, 60)
    return count > 30
