import os

import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware import AgeLimit, AsyncIO, Retries
from dramatiq.middleware.prometheus import Prometheus


def build_broker() -> RedisBroker:
    return RedisBroker(  # type: ignore[no-untyped-call]
        url=os.getenv("CARVEO_REDIS_URL", "redis://localhost:6379/0"),
        middleware=[
            AgeLimit(max_age=300_000),
            AsyncIO(),
            Prometheus(),
            Retries(max_retries=3, min_backoff=1_000, max_backoff=30_000),
        ],
    )


def configure_broker(broker: dramatiq.Broker | None = None) -> dramatiq.Broker:
    configured = broker or build_broker()
    dramatiq.set_broker(configured)
    return configured
