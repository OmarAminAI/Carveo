import dramatiq

from carveo_worker.broker import configure_broker

broker = configure_broker()


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


def configure_worker_broker(configured: dramatiq.Broker) -> None:
    global broker
    broker = configure_broker(configured)
    smoke.broker = broker
    broker.declare_actor(smoke)
