import dramatiq
from carveo_worker.tasks import configure_worker_broker, smoke
from dramatiq.brokers.stub import StubBroker
from dramatiq.middleware import AsyncIO, Retries
from dramatiq.worker import Worker


def test_smoke_actor_enqueues_json_safe_message() -> None:
    broker = StubBroker()
    configure_worker_broker(broker)

    message = smoke.send("probe-123")

    assert message.args == ("probe-123",)
    assert smoke.options["max_retries"] == 3
    assert smoke.options["max_age"] == 300_000
    assert broker.get_declared_queues() == {"ingestion", "ingestion.DQ"}
    dramatiq.set_broker(broker)


def test_failed_actor_is_dead_lettered_after_retry_exhaustion() -> None:
    broker = StubBroker(middleware=[AsyncIO(), Retries()])
    configure_worker_broker(broker)
    worker = Worker(broker, worker_timeout=100)
    worker.start()
    try:
        smoke.send_with_options(args=("",), max_retries=0)
        broker.join("ingestion", timeout=5_000, fail_fast=False)
    finally:
        worker.stop()
        worker.join()

    assert len(broker.dead_letters) == 1
