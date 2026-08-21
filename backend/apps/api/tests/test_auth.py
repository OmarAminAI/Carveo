from collections.abc import AsyncIterator

import httpx
import pytest
from carveo_api.auth import (
    AuthenticatedBuyer,
    AuthenticationError,
    AuthenticationUnavailableError,
    ClerkRequestAuthenticator,
)
from carveo_api.main import create_app
from carveo_api.settings import Settings
from clerk_backend_api.security.types import AuthStatus, RequestState
from pydantic import ValidationError
from starlette.requests import Request


class FakeAuthenticator:
    def __init__(self, clerk_user_id: str) -> None:
        self.clerk_user_id = clerk_user_id

    async def authenticate(self, request: Request) -> AuthenticatedBuyer:
        token = request.headers.get("Authorization")
        if token == "Bearer unavailable":
            raise AuthenticationUnavailableError
        if token != "Bearer verified":
            raise AuthenticationError
        return AuthenticatedBuyer(clerk_user_id=self.clerk_user_id)


class FakeClerkClient:
    def __init__(self, state: RequestState | Exception) -> None:
        self.state = state

    def authenticate_request(self, request: Request, options: object) -> RequestState:
        if isinstance(self.state, Exception):
            raise self.state
        return self.state


@pytest.fixture
async def auth_client() -> AsyncIterator[httpx.AsyncClient]:
    app = create_app(authenticator=FakeAuthenticator("user_clerk_1"), readiness_check=lambda: ready())
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client


@pytest.mark.anyio
async def test_missing_token_returns_unauthorized_problem(auth_client: httpx.AsyncClient) -> None:
    response = await auth_client.get("/api/v1/me/workspace")

    assert response.status_code == 401
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["type"].endswith("/authentication-required")


@pytest.mark.anyio
async def test_verified_subject_is_returned_without_client_identity() -> None:
    request = Request(
        {"type": "http", "method": "GET", "path": "/", "headers": [(b"authorization", b"Bearer verified")]}
    )

    buyer = await FakeAuthenticator("user_clerk_1").authenticate(request)

    assert buyer.clerk_user_id == "user_clerk_1"


@pytest.mark.anyio
async def test_verified_request_returns_only_clerk_subject(auth_client: httpx.AsyncClient) -> None:
    response = await auth_client.get("/api/v1/me/workspace", headers={"Authorization": "Bearer verified"})

    assert response.status_code == 200
    assert response.json() == {"clerkUserId": "user_clerk_1"}


@pytest.mark.anyio
async def test_clerk_authenticator_returns_only_verified_nonempty_subject() -> None:
    request = Request({"type": "http", "method": "GET", "path": "/", "headers": []})
    authenticator = ClerkRequestAuthenticator("sk_test_123", ["http://localhost:3000"])
    authenticator._clerk = FakeClerkClient(
        RequestState(status=AuthStatus.SIGNED_IN, token="token", payload={"sub": "user_clerk_1"})
    )

    buyer = await authenticator.authenticate(request)

    assert buyer == AuthenticatedBuyer(clerk_user_id="user_clerk_1")


@pytest.mark.anyio
async def test_clerk_authenticator_maps_unsigned_or_malformed_subjects_to_one_authentication_error() -> None:
    request = Request({"type": "http", "method": "GET", "path": "/", "headers": []})
    authenticator = ClerkRequestAuthenticator("sk_test_123", ["http://localhost:3000"])
    authenticator._clerk = FakeClerkClient(RequestState(status=AuthStatus.SIGNED_OUT))

    with pytest.raises(AuthenticationError):
        await authenticator.authenticate(request)


@pytest.mark.anyio
async def test_clerk_authenticator_maps_sdk_failures_to_unavailable() -> None:
    request = Request({"type": "http", "method": "GET", "path": "/", "headers": []})
    authenticator = ClerkRequestAuthenticator("sk_test_123", ["http://localhost:3000"])
    authenticator._clerk = FakeClerkClient(RuntimeError("jwks unavailable"))

    with pytest.raises(AuthenticationUnavailableError):
        await authenticator.authenticate(request)


@pytest.mark.anyio
async def test_invalid_authentication_has_the_same_sanitized_problem(auth_client: httpx.AsyncClient) -> None:
    response = await auth_client.get("/api/v1/me/workspace", headers={"Authorization": "Bearer invalid"})

    assert response.status_code == 401
    assert response.json()["type"].endswith("/authentication-required")
    assert "invalid" not in response.text


@pytest.mark.anyio
async def test_authentication_unavailable_is_sanitized_and_does_not_affect_readiness(
    auth_client: httpx.AsyncClient,
) -> None:
    unavailable = await auth_client.get("/api/v1/me/workspace", headers={"Authorization": "Bearer unavailable"})
    readiness = await auth_client.get("/ready")

    assert unavailable.status_code == 503
    assert unavailable.json()["type"].endswith("/authentication-unavailable")
    assert readiness.json() == {"status": "ready"}


@pytest.mark.anyio
async def test_authentication_unavailable_log_does_not_include_sdk_exception_details(
    capsys: pytest.CaptureFixture[str],
) -> None:
    secret_error = "clerk-sdk-secret-token"
    authenticator = ClerkRequestAuthenticator("sk_test_123", ["http://localhost:3000"])
    authenticator._clerk = FakeClerkClient(RuntimeError(secret_error))
    app = create_app(authenticator=authenticator, readiness_check=lambda: ready())

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as test_client:
        response = await test_client.get("/api/v1/me/workspace")

    log_output = capsys.readouterr().out

    assert response.status_code == 503
    assert "authentication verification failed" in log_output
    assert secret_error not in log_output
    assert "Traceback" not in log_output


def test_production_requires_explicit_clerk_authorized_parties_and_a_verification_key() -> None:
    settings = {
        "environment": "production",
        "database_url": "postgresql+psycopg://service:password@localhost:5432/carveo",
        "cors_origins": ["https://app.carveo.example"],
    }

    with pytest.raises(ValidationError, match="CLERK_AUTHORIZED_PARTIES"):
        Settings(**settings)

    with pytest.raises(ValidationError, match="CLERK_SECRET_KEY or CLERK_JWT_KEY"):
        Settings(**(settings | {"clerk_authorized_parties": ["https://app.carveo.example"]}))

    assert Settings(
        **(
            settings
            | {
                "clerk_authorized_parties": ["https://app.carveo.example"],
                "clerk_jwt_key": "public-key",
            }
        )
    ).clerk_jwt_key == "public-key"


async def ready() -> bool:
    return True
