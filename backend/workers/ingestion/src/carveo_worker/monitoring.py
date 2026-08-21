"""Scheduled health monitoring for Carveo services."""

from __future__ import annotations

import logging
import time
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass

import httpx
from prometheus_client import REGISTRY, CollectorRegistry, Gauge
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from carveo_worker.beat_health import is_fresh_heartbeat
from carveo_worker.tasks import WORKER_HEARTBEAT_KEY, heartbeat

Probe = Callable[[], Awaitable[bool]]


@dataclass(frozen=True)
class ProbeResult:
    target: str
    up: bool
    duration_seconds: float
    error: str | None = None


class HealthMonitor:
    def __init__(self, probes: Mapping[str, Probe], *, registry: CollectorRegistry = REGISTRY) -> None:
        self._probes = dict(probes)
        self._logger = logging.getLogger("carveo.beat")
        self._target_up = Gauge(
            "carveo_health_target_up",
            "Whether the latest Carveo health target probe succeeded.",
            ("target",),
            registry=registry,
        )
        self._probe_duration = Gauge(
            "carveo_health_probe_duration_seconds",
            "Duration of the latest Carveo health target probe.",
            ("target",),
            registry=registry,
        )
        self._last_success = Gauge(
            "carveo_health_last_success_timestamp_seconds",
            "Unix timestamp of the latest successful Carveo target probe.",
            ("target",),
            registry=registry,
        )

    async def run_cycle(self) -> dict[str, ProbeResult]:
        results: dict[str, ProbeResult] = {}
        for target, probe in self._probes.items():
            started_at = time.perf_counter()
            error: str | None = None
            try:
                up = bool(await probe())
            except Exception as exc:
                up = False
                error = type(exc).__name__
                self._logger.warning(
                    "health probe failed",
                    extra={"target": target, "error_type": error},
                )
            duration = time.perf_counter() - started_at
            result = ProbeResult(target=target, up=up, duration_seconds=duration, error=error)
            results[target] = result
            self._target_up.labels(target).set(1 if up else 0)
            self._probe_duration.labels(target).set(duration)
            if up:
                self._last_success.labels(target).set(time.time())
        return results


async def probe_http(client: httpx.AsyncClient, url: str) -> bool:
    response = await client.get(url)
    response.raise_for_status()
    return True


async def probe_redis(client: Redis) -> bool:
    return bool(await client.ping())


async def probe_postgres(engine: AsyncEngine) -> bool:
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))
    return True


async def probe_worker(
    client: Redis,
    *,
    delay_seconds: float,
    max_age_seconds: int,
    sleep: Callable[[float], Awaitable[None]],
) -> bool:
    import uuid

    heartbeat.send(str(uuid.uuid4()))
    await sleep(delay_seconds)
    value = await client.get(WORKER_HEARTBEAT_KEY)
    if isinstance(value, bytes):
        value = value.decode()
    return is_fresh_heartbeat(value, now=time.time(), max_age_seconds=max_age_seconds)
