import asyncio
import os

from redis.asyncio import Redis


async def check() -> None:
    client = Redis.from_url(os.getenv("CARVEO_REDIS_URL", "redis://localhost:6379/0"))
    try:
        if not await client.ping():
            raise RuntimeError("Redis ping failed")
    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(check())
