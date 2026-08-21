from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, cast

import anyio
from clerk_backend_api import Clerk
from clerk_backend_api.security.types import AuthenticateRequestOptions
from fastapi import Request


@dataclass(frozen=True)
class AuthenticatedBuyer:
    clerk_user_id: str


class AuthenticationError(Exception):
    pass


class AuthenticationUnavailableError(Exception):
    pass


class RequestAuthenticator(Protocol):
    async def authenticate(self, request: Request) -> AuthenticatedBuyer: ...


class ClerkRequestAuthenticator:
    def __init__(self, secret_key: str | None, authorized_parties: list[str], jwt_key: str | None = None) -> None:
        self._clerk = Clerk(bearer_auth=secret_key)
        self._options = AuthenticateRequestOptions(authorized_parties=authorized_parties, jwt_key=jwt_key)

    async def authenticate(self, request: Request) -> AuthenticatedBuyer:
        return await anyio.to_thread.run_sync(self._authenticate_sync, request)

    def _authenticate_sync(self, request: Request) -> AuthenticatedBuyer:
        try:
            state = self._clerk.authenticate_request(request, self._options)
        except Exception as exc:
            raise AuthenticationUnavailableError from exc

        subject = state.payload.get("sub") if state.is_signed_in and state.payload is not None else None
        if not isinstance(subject, str) or not subject:
            raise AuthenticationError
        return AuthenticatedBuyer(clerk_user_id=subject)


async def require_buyer(request: Request) -> AuthenticatedBuyer:
    authenticator = cast(RequestAuthenticator, request.app.state.authenticator)
    return await authenticator.authenticate(request)
