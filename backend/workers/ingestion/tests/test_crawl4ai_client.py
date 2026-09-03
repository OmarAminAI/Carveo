from __future__ import annotations

import json

import httpx
import pytest
from carveo_worker.crawl4ai_client import Crawl4AIClient

pytestmark = pytest.mark.anyio


def crawl_result(url: str, *, success: bool = True, error: str | None = None) -> dict[str, object]:
    return {
        "url": url,
        "html": "<html><body>vehicle</body></html>",
        "status_code": 200,
        "success": success,
        "error_message": error,
    }


async def test_client_authenticates_uses_non_streaming_batches_and_preserves_order() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        payload = json.loads(request.content)
        return httpx.Response(200, json={"results": [crawl_result(url) for url in payload["urls"]]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://crawl4ai:11235") as http:
        client = Crawl4AIClient(http=http, token="secret-token", max_batch_size=2)
        documents = await client.crawl(
            [
                "http://fixture-origin:8080/listings/fixture-001.html",
                "http://fixture-origin:8080/listings/fixture-002.html",
                "http://fixture-origin:8080/listings/fixture-003.html",
            ]
        )

    assert [document.url for document in documents] == [
        "http://fixture-origin:8080/listings/fixture-001.html",
        "http://fixture-origin:8080/listings/fixture-002.html",
        "http://fixture-origin:8080/listings/fixture-003.html",
    ]
    assert len(requests) == 2
    assert all(request.method == "POST" and request.url.path == "/crawl" for request in requests)
    assert all(request.headers["authorization"] == "Bearer secret-token" for request in requests)
    payloads = [json.loads(request.content) for request in requests]
    assert [payload["urls"] for payload in payloads] == [
        [
            "http://fixture-origin:8080/listings/fixture-001.html",
            "http://fixture-origin:8080/listings/fixture-002.html",
        ],
        ["http://fixture-origin:8080/listings/fixture-003.html"],
    ]
    assert all(payload["crawler_config"]["stream"] is False for payload in payloads)
    assert all(request.extensions["timeout"]["read"] < 60 for request in requests)


@pytest.mark.parametrize(
    ("exception", "expected_error"),
    [
        (httpx.ConnectTimeout("cannot connect"), "unavailable"),
        (httpx.ReadTimeout("slow response"), "timeout"),
    ],
)
async def test_client_classifies_transport_failures_without_leaking_details(
    exception: httpx.HTTPError,
    expected_error: str,
) -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        raise exception

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://crawl4ai:11235") as http:
        documents = await Crawl4AIClient(http=http, token="secret-token").crawl(
            ["http://fixture-origin:8080/listings/fixture-001.html"]
        )

    assert documents[0].success is False
    assert documents[0].error == expected_error
    assert "secret-token" not in repr(documents[0])
    assert str(exception) not in repr(documents[0])


@pytest.mark.parametrize(
    ("status_code", "expected_error"),
    [(401, "authentication"), (403, "authentication"), (429, "rate_limited"), (500, "server_error")],
)
async def test_client_classifies_http_failures(status_code: int, expected_error: str) -> None:
    transport = httpx.MockTransport(lambda _: httpx.Response(status_code, text="upstream private details"))
    async with httpx.AsyncClient(transport=transport, base_url="http://crawl4ai:11235") as http:
        documents = await Crawl4AIClient(http=http, token="secret-token").crawl(
            ["http://fixture-origin:8080/listings/fixture-001.html"]
        )

    assert documents[0].error == expected_error
    assert "private details" not in repr(documents[0])


async def test_client_classifies_antibot_result_as_blocked() -> None:
    url = "http://fixture-origin:8080/listings/fixture-001.html"
    result = crawl_result(url, success=False, error="Navigation failed: CAPTCHA challenge detected")
    transport = httpx.MockTransport(lambda _: httpx.Response(200, json={"results": [result]}))
    async with httpx.AsyncClient(transport=transport, base_url="http://crawl4ai:11235") as http:
        documents = await Crawl4AIClient(http=http, token="secret-token").crawl([url])

    assert documents[0].error == "blocked"
    assert "CAPTCHA" not in repr(documents[0])


@pytest.mark.parametrize(
    "response",
    [
        httpx.Response(200, text="not-json"),
        httpx.Response(200, json={"results": []}),
        httpx.Response(
            200,
            json={
                "results": [crawl_result("http://fixture-origin:8080/listings/a-different-listing.html")]
            },
        ),
    ],
)
async def test_client_rejects_malformed_missing_or_mismatched_results(response: httpx.Response) -> None:
    url = "http://fixture-origin:8080/listings/fixture-001.html"
    transport = httpx.MockTransport(lambda _: response)
    async with httpx.AsyncClient(transport=transport, base_url="http://crawl4ai:11235") as http:
        documents = await Crawl4AIClient(http=http, token="secret-token").crawl([url])

    assert documents[0].url == url
    assert documents[0].success is False
    assert documents[0].error == "invalid_response"
