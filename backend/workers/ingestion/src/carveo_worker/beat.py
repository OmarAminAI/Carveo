"""Carveo periodic scheduler entry point."""

from __future__ import annotations

import asyncio
import logging
import os
import signal
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Protocol

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore[import-untyped]
from carveo_core.database import create_engine
from prometheus_client import Gauge, start_http_server
from redis.asyncio import Redis

from carveo_worker.logging import configure_logging
from carveo_worker.monitoring import HealthMonitor, probe_http, probe_postgres, probe_redis, probe_worker

BEAT_HEARTBEAT_KEY = "carveo:beat:last_tick"
BEAT_LAST_TICK = Gauge(
    "carveo_beat_last_tick_timestamp_seconds",
    "Unix timestamp of the latest completed Carveo Beat health cycle.",
)


class BeatStore(Protocol):
    async def set(self, key: str, value: str, *, ex: int) -> object: ...


@dataclass(frozen=True)
class BeatSettings:
    redis_url: str
    database_url: str
    api_ready_url: str
    web_ready_url: str
    crawl4ai_health_url: str
    prometheus_ready_url: str
    grafana_health_url: str
    interval_seconds: int = 30
    heartbeat_ttl_seconds: int = 90
    worker_probe_delay_seconds: float = 0.5
    metrics_port: int = 9108

    @classmethod
    def from_env(cls) -> BeatSettings:
        return cls(
            redis_url=os.getenv("CARVEO_REDIS_URL", "redis://localhost:6379/0"),
            database_url=os.getenv(
                "CARVEO_DATABASE_URL", "postgresql+psycopg://carveo:carveo@localhost:5432/carveo"
            ),
            api_ready_url=os.getenv("CARVEO_API_READY_URL", "http://api:8000/ready"),
            web_ready_url=os.getenv("CARVEO_WEB_READY_URL", "http://web:3000/api/ready"),
            crawl4ai_health_url=os.getenv("CARVEO_CRAWL4AI_HEALTH_URL", "http://crawl4ai:11235/health"),
            prometheus_ready_url=os.getenv("CARVEO_PROMETHEUS_READY_URL", "http://prometheus:9090/-/ready"),
            grafana_health_url=os.getenv("CARVEO_GRAFANA_HEALTH_URL", "http://grafana:3000/api/health"),
            interval_seconds=int(os.getenv("CARVEO_BEAT_INTERVAL_SECONDS", "30")),
            heartbeat_ttl_seconds=int(os.getenv("CARVEO_BEAT_HEARTBEAT_TTL_SECONDS", "90")),
            worker_probe_delay_seconds=float(os.getenv("CARVEO_WORKER_PROBE_DELAY_SECONDS", "0.5")),
            metrics_port=int(os.getenv("CARVEO_BEAT_METRICS_PORT", "9108")),
        )


class BeatRuntime:
    def __init__(self, settings: BeatSettings) -> None:
        self.settings = settings
        self.http = httpx.AsyncClient(timeout=5)
        self.redis = Redis.from_url(settings.redis_url)
        self.engine = create_engine(settings.database_url)
        self.monitor = HealthMonitor(
            {
                "api": lambda: probe_http(self.http, settings.api_ready_url),
                "web": lambda: probe_http(self.http, settings.web_ready_url),
                "crawl4ai": lambda: probe_http(self.http, settings.crawl4ai_health_url),
                "prometheus": lambda: probe_http(self.http, settings.prometheus_ready_url),
                "grafana": lambda: probe_http(self.http, settings.grafana_health_url),
                "redis": lambda: probe_redis(self.redis),
                "postgres": lambda: probe_postgres(self.engine),
                "worker": lambda: probe_worker(
                    self.redis,
                    delay_seconds=settings.worker_probe_delay_seconds,
                    max_age_seconds=settings.heartbeat_ttl_seconds,
                    sleep=asyncio.sleep,
                ),
            }
        )

    async def run_cycle(self) -> None:
        results = await self.monitor.run_cycle()
        now = time.time()
        await record_beat_tick(
            self.redis,
            now=now,
            ttl_seconds=self.settings.heartbeat_ttl_seconds,
        )
        BEAT_LAST_TICK.set(now)
        logging.getLogger("carveo.beat").info(
            "health cycle complete",
            extra={
                "healthy_targets": sum(result.up for result in results.values()),
                "target_count": len(results),
            },
        )

    async def close(self) -> None:
        await self.http.aclose()
        await self.redis.aclose()
        await self.engine.dispose()


async def record_beat_tick(store: BeatStore, *, now: float, ttl_seconds: int) -> None:
    await store.set(BEAT_HEARTBEAT_KEY, str(now), ex=ttl_seconds)


def build_scheduler(
    job: Callable[[], Awaitable[None] | None], *, interval_seconds: int
) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        job,
        "interval",
        seconds=interval_seconds,
        id="health-monitor",
        coalesce=True,
        max_instances=1,
        replace_existing=True,
    )
    return scheduler


async def run() -> None:
    settings = BeatSettings.from_env()
    configure_logging(os.getenv("CARVEO_LOG_LEVEL", "INFO"))
    start_http_server(settings.metrics_port, addr="0.0.0.0")
    runtime = BeatRuntime(settings)
    scheduler = build_scheduler(runtime.run_cycle, interval_seconds=settings.interval_seconds)
    stopped = asyncio.Event()
    loop = asyncio.get_running_loop()
    for signal_name in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(signal_name, stopped.set)
    try:
        await runtime.run_cycle()
        scheduler.start()
        await stopped.wait()
    finally:
        if scheduler.running:
            scheduler.shutdown(wait=False)
        await runtime.close()


if __name__ == "__main__":
    asyncio.run(run())
