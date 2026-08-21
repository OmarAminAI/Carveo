"""Docker health command for the Carveo scheduler."""

import asyncio
import os
import time

from redis.asyncio import Redis

BEAT_HEARTBEAT_KEY = "carveo:beat:last_tick"


def is_fresh_heartbeat(value: str | None, *, now: float, max_age_seconds: int) -> bool:
    if value is None:
        return False
    try:
        timestamp = float(value)
    except ValueError:
        return False
    age = now - timestamp
    return 0 <= age <= max_age_seconds


async def check() -> None:
    client = Redis.from_url(os.getenv("CARVEO_REDIS_URL", "redis://localhost:6379/0"))
    try:
        value = await client.get(BEAT_HEARTBEAT_KEY)
        if isinstance(value, bytes):
            value = value.decode()
        max_age = int(os.getenv("CARVEO_BEAT_HEARTBEAT_TTL_SECONDS", "90"))
        if not is_fresh_heartbeat(value, now=time.time(), max_age_seconds=max_age):
            raise RuntimeError("Beat heartbeat is missing or stale")
    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(check())
