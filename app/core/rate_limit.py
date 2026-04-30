import time
from dataclasses import dataclass

from fastapi import HTTPException, Request, status
from redis.exceptions import RedisError

from app.core.config import settings


@dataclass
class RateLimitPolicy:
    name: str
    limit: int
    window_seconds: int


REGISTER_LIMIT = RateLimitPolicy(name="register", limit=3, window_seconds=60)
LOGIN_LIMIT = RateLimitPolicy(name="login", limit=5, window_seconds=60)


class RedisRateLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client

    def _key(self, policy: RateLimitPolicy, identifier: str) -> str:
        bucket = int(time.time() // policy.window_seconds)
        return f"ratelimit:{policy.name}:{identifier}:{bucket}"

    def hit(self, policy: RateLimitPolicy, identifier: str):
        key = self._key(policy, identifier)
        count = self.redis.incr(key)
        if count == 1:
            self.redis.expire(key, policy.window_seconds)
        ttl = self.redis.ttl(key)
        return count, max(ttl, 0)


def get_client_identifier(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def enforce_rate_limit(request: Request, limiter: RedisRateLimiter, policy: RateLimitPolicy):
    if not settings.RATE_LIMIT_ENABLED:
        return

    identifier = get_client_identifier(request)

    try:
        count, ttl = limiter.hit(policy, identifier)
    except RedisError:
        if settings.RATE_LIMIT_FAIL_OPEN:
            return
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rate limit service unavailable",
        )

    if count > policy.limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": "Rate limit exceeded",
                "policy": policy.name,
                "retry_after": ttl,
            },
        )