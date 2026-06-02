import redis.asyncio as aioredis
from fastapi import Request, HTTPException, status

from app.core.security import decode_token
from app.core.config import settings


async def verify_token(request: Request) -> int:
    authorization = request.headers.get("Authorization")

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )

    token = authorization.split(" ")[1]

    try:
        payload = decode_token(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    redis = await aioredis.from_url(settings.REDIS_URL)
    is_blacklisted = await redis.get(f"blacklist:{token}")
    await redis.aclose()

    if is_blacklisted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )

    return int(payload["sub"])