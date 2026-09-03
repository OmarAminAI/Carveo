from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Literal

import httpx
from pydantic import BaseModel, ConfigDict, Field

CrawlError = Literal[
    "authentication",
    "blocked",
    "invalid_response",
    "navigation_failure",
    "rate_limited",
    "server_error",
    "timeout",
    "unavailable",
]


class CrawlDocument(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    url: str = Field(min_length=1, max_length=2048)
    html: str
    status_code: int | None = Field(default=None, ge=100, le=599)
    success: bool
    error: CrawlError | None = None


class Crawl4AIClient:
    def __init__(
        self,
        *,
        http: httpx.AsyncClient,
        token: str,
        max_batch_size: int = 10,
        timeout_seconds: float = 20.0,
    ) -> None:
        if not token:
            raise ValueError("Crawl4AI token is required")
        if not 1 <= max_batch_size <= 32:
            raise ValueError("max_batch_size must be between 1 and 32")
        if not 0 < timeout_seconds <= 60:
            raise ValueError("timeout_seconds must be between 0 and 60")
        self._http = http
        self._token = token
        self._max_batch_size = max_batch_size
        self._timeout = httpx.Timeout(timeout_seconds)

    async def crawl(self, urls: Sequence[str]) -> list[CrawlDocument]:
        ordered_urls = list(urls)
        documents: list[CrawlDocument] = []
        for offset in range(0, len(ordered_urls), self._max_batch_size):
            batch = ordered_urls[offset : offset + self._max_batch_size]
            documents.extend(await self._crawl_batch(batch))
        return documents

    async def _crawl_batch(self, urls: list[str]) -> list[CrawlDocument]:
        try:
            response = await self._http.post(
                "/crawl",
                headers={"Authorization": f"Bearer {self._token}"},
                json={
                    "urls": urls,
                    "browser_config": {"type": "BrowserConfig", "headless": True},
                    "crawler_config": {"type": "CrawlerRunConfig", "stream": False},
                },
                timeout=self._timeout,
            )
        except httpx.ConnectTimeout:
            return self._fail_all(urls, "unavailable")
        except httpx.ReadTimeout:
            return self._fail_all(urls, "timeout")
        except httpx.RequestError:
            return self._fail_all(urls, "unavailable")

        http_error = self._classify_status(response.status_code)
        if http_error is not None:
            return self._fail_all(urls, http_error, response.status_code)

        try:
            payload = response.json()
        except ValueError:
            return self._fail_all(urls, "invalid_response", response.status_code)
        if not isinstance(payload, Mapping):
            return self._fail_all(urls, "invalid_response", response.status_code)
        results = payload.get("results")
        if not isinstance(results, list) or len(results) != len(urls):
            return self._fail_all(urls, "invalid_response", response.status_code)

        decoded: list[CrawlDocument] = []
        for expected_url, raw_result in zip(urls, results, strict=True):
            if not isinstance(raw_result, Mapping) or raw_result.get("url") != expected_url:
                return self._fail_all(urls, "invalid_response", response.status_code)
            document = self._decode_result(expected_url, raw_result)
            if document is None:
                return self._fail_all(urls, "invalid_response", response.status_code)
            decoded.append(document)
        return decoded

    @staticmethod
    def _classify_status(status_code: int) -> CrawlError | None:
        if status_code in {401, 403}:
            return "authentication"
        if status_code == 429:
            return "rate_limited"
        if status_code >= 500:
            return "server_error"
        if status_code >= 400:
            return "invalid_response"
        return None

    @staticmethod
    def _decode_result(url: str, result: Mapping[object, object]) -> CrawlDocument | None:
        success = result.get("success")
        html = result.get("html", "")
        status_code = result.get("status_code")
        if not isinstance(success, bool) or not isinstance(html, str):
            return None
        if status_code is not None and (not isinstance(status_code, int) or isinstance(status_code, bool)):
            return None
        if success:
            return CrawlDocument(url=url, html=html, status_code=status_code, success=True)

        raw_error = result.get("error_message", result.get("error", ""))
        error_text = raw_error if isinstance(raw_error, str) else ""
        evidence = f"{error_text} {html}".lower()
        if any(marker in evidence for marker in ("captcha", "access denied", "cloudflare", "anti-bot", "blocked")):
            error: CrawlError = "blocked"
        else:
            error = "navigation_failure"
        return CrawlDocument(url=url, html="", status_code=status_code, success=False, error=error)

    @staticmethod
    def _fail_all(
        urls: Sequence[str],
        error: CrawlError,
        status_code: int | None = None,
    ) -> list[CrawlDocument]:
        return [
            CrawlDocument(url=url, html="", status_code=status_code, success=False, error=error)
            for url in urls
        ]
