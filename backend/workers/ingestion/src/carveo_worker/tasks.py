import os
import time

import dramatiq
from redis.asyncio import Redis

from carveo_worker.broker import configure_broker
from carveo_worker.logging import configure_logging

configure_logging(os.getenv("CARVEO_LOG_LEVEL", "INFO"))
broker = configure_broker()
WORKER_HEARTBEAT_KEY = "carveo:worker:last_heartbeat"


@dramatiq.actor(
    broker=broker,
    queue_name="ingestion",
    max_retries=3,
    min_backoff=1_000,
    max_backoff=30_000,
    max_age=300_000,
)
async def smoke(probe_id: str) -> None:
    if not probe_id.strip():
        raise ValueError("probe_id must be non-empty")


@dramatiq.actor(
    broker=broker,
    queue_name="operations",
    max_retries=3,
    min_backoff=1_000,
    max_backoff=30_000,
    max_age=300_000,
)
async def heartbeat(probe_id: str) -> None:
    if not probe_id.strip():
        raise ValueError("probe_id must be non-empty")
    client = Redis.from_url(os.getenv("CARVEO_REDIS_URL", "redis://localhost:6379/0"))
    try:
        await client.set(WORKER_HEARTBEAT_KEY, str(time.time()), ex=90)
    finally:
        await client.aclose()


def configure_worker_broker(configured: dramatiq.Broker) -> None:
    global broker
    broker = configure_broker(configured)
    for actor in (smoke, heartbeat):
        actor.broker = broker
        broker.declare_actor(actor)
