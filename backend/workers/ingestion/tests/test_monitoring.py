import httpx
import pytest
from carveo_worker import beat, beat_health, monitoring
from prometheus_client import CollectorRegistry, generate_latest


def test_monitoring_interfaces_are_available() -> None:
    assert hasattr(monitoring, "HealthMonitor")
    assert hasattr(beat_health, "is_fresh_heartbeat")
    assert hasattr(beat, "build_scheduler")


@pytest.mark.anyio
async def test_health_monitor_records_failures_without_aborting_the_cycle() -> None:
    async def healthy() -> bool:
        return True

    async def unavailable() -> bool:
        raise RuntimeError("connection refused")

    registry = CollectorRegistry()
    monitor = monitoring.HealthMonitor({"api": healthy, "crawl4ai": unavailable}, registry=registry)

    results = await monitor.run_cycle()
    metrics = generate_latest(registry).decode()

    assert results["api"].up is True
    assert results["crawl4ai"].up is False
    assert results["crawl4ai"].error == "RuntimeError"
    assert 'carveo_health_target_up{target="api"} 1.0' in metrics
    assert 'carveo_health_target_up{target="crawl4ai"} 0.0' in metrics


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, False),
        ("not-a-timestamp", False),
        ("900.0", False),
        ("950.0", True),
        ("1001.0", False),
    ],
)
def test_beat_heartbeat_must_be_recent_and_not_from_the_future(value: str | None, expected: bool) -> None:
    assert beat_health.is_fresh_heartbeat(value, now=1_000.0, max_age_seconds=90) is expected


def test_scheduler_job_is_coalesced_and_non_overlapping() -> None:
    scheduler = beat.build_scheduler(lambda: None, interval_seconds=30)

    job = scheduler.get_job("health-monitor")

    assert job is not None
    assert job.coalesce is True
    assert job.max_instances == 1


@pytest.mark.anyio
async def test_http_probe_rejects_unsuccessful_responses() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(httpx.HTTPStatusError):
            await monitoring.probe_http(client, "http://service/ready")


@pytest.mark.anyio
async def test_beat_tick_uses_a_bounded_redis_ttl() -> None:
    class FakeRedis:
        def __init__(self) -> None:
            self.write: tuple[str, str, int] | None = None

        async def set(self, key: str, value: str, *, ex: int) -> None:
            self.write = (key, value, ex)

    redis = FakeRedis()

    await beat.record_beat_tick(redis, now=1_000.0, ttl_seconds=90)

    assert redis.write == ("carveo:beat:last_tick", "1000.0", 90)
