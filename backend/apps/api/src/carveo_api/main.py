from __future__ import annotations

import logging
import time
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable

from carveo_core.catalogue import CatalogueRepository
from carveo_core.contracts import (
    CompareRequest,
    CompareResponse,
    Listing,
    ListingPage,
    ListingQuery,
    Market,
    ModelInsights,
)
from carveo_core.database import create_engine, create_session_factory
from carveo_core.sql_repository import SqlAlchemyCatalogueRepository
from fastapi import Depends, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import JSONResponse, Response

from carveo_api.auth import (
    AuthenticatedBuyer,
    AuthenticationError,
    AuthenticationUnavailableError,
    ClerkRequestAuthenticator,
    RequestAuthenticator,
    require_buyer,
)
from carveo_api.logging import configure_logging
from carveo_api.problems import problem, validation_problem
from carveo_api.settings import get_settings

ReadinessCheck = Callable[[], Awaitable[bool]]

REQUESTS = Counter(
    "carveo_api_http_requests_total",
    "Total HTTP requests handled by the Carveo API.",
    ("method", "route", "status"),
)
REQUEST_DURATION = Histogram(
    "carveo_api_http_request_duration_seconds",
    "Carveo API request duration in seconds.",
    ("method", "route"),
)


def listing_query(
    market: str = "ae",
    q: str = "",
    make: list[str] = Query(default=[]),
    model: list[str] = Query(default=[]),
    body_type: list[str] = Query(default=[], alias="bodyType"),
    year_min: int | None = Query(default=None, alias="yearMin"),
    year_max: int | None = Query(default=None, alias="yearMax"),
    price_min: int | None = Query(default=None, alias="priceMin"),
    price_max: int | None = Query(default=None, alias="priceMax"),
    mileage_max: int | None = Query(default=None, alias="mileageMax"),
    specifications: list[str] = Query(default=[]),
    seller_type: list[str] = Query(default=[], alias="sellerType"),
    evidence: list[str] = Query(default=[]),
    city: list[str] = Query(default=[]),
    sort: str = "best-match",
    page: int = 1,
    page_size: int = Query(default=12, alias="pageSize"),
) -> ListingQuery:
    try:
        return ListingQuery.model_validate(
            {
                "market": market,
                "q": q,
                "make": make,
                "model": model,
                "body_type": body_type,
                "year_min": year_min,
                "year_max": year_max,
                "price_min": price_min,
                "price_max": price_max,
                "mileage_max": mileage_max,
                "specifications": specifications,
                "seller_type": seller_type,
                "evidence": evidence,
                "city": city,
                "sort": sort,
                "page": page,
                "page_size": page_size,
            }
        )
    except ValidationError as exc:
        raise RequestValidationError(exc.errors()) from exc


def create_app(
    *,
    repository: CatalogueRepository | None = None,
    readiness_check: ReadinessCheck | None = None,
    authenticator: RequestAuthenticator | None = None,
) -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)
    app = FastAPI(title="Carveo Catalogue API", version="1.0.0")
    app.state.authenticator = authenticator or ClerkRequestAuthenticator(
        settings.clerk_secret_key,
        settings.clerk_authorized_parties,
        settings.clerk_jwt_key,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "X-Request-ID"],
    )

    async def request_validation_problem(request: Request, exc: Exception) -> JSONResponse:
        assert isinstance(exc, RequestValidationError)
        return await validation_problem(request, exc)

    app.add_exception_handler(RequestValidationError, request_validation_problem)

    async def authentication_problem(request: Request, exc: Exception) -> JSONResponse:
        assert isinstance(exc, AuthenticationError)
        return problem(
            status=401,
            slug="authentication-required",
            title="Authentication required",
            detail="A valid buyer session is required.",
            instance=request.url.path,
        )

    app.add_exception_handler(AuthenticationError, authentication_problem)

    async def authentication_unavailable_problem(request: Request, exc: Exception) -> JSONResponse:
        assert isinstance(exc, AuthenticationUnavailableError)
        logging.getLogger("carveo.api").exception("authentication verification failed")
        return problem(
            status=503,
            slug="authentication-unavailable",
            title="Authentication unavailable",
            detail="Authentication could not be verified.",
            instance=request.url.path,
        )

    app.add_exception_handler(AuthenticationUnavailableError, authentication_unavailable_problem)

    async def database_problem(request: Request, exc: Exception) -> JSONResponse:
        assert isinstance(exc, SQLAlchemyError)
        logging.getLogger("carveo.api").exception("database request failed")
        return problem(
            status=503,
            slug="database-unavailable",
            title="Database unavailable",
            detail="The catalogue database could not complete the request.",
            instance=request.url.path,
        )

    app.add_exception_handler(SQLAlchemyError, database_problem)

    async def internal_problem(request: Request, exc: Exception) -> JSONResponse:
        logging.getLogger("carveo.api").exception(
            "unhandled request failure",
            extra={"method": request.method, "path": request.url.path},
        )
        return problem(
            status=500,
            slug="internal-error",
            title="Internal server error",
            detail="The request could not be completed.",
            instance=request.url.path,
        )

    app.add_exception_handler(Exception, internal_problem)
    engine = None if repository else create_engine(settings.database_url)
    session_factory = None if engine is None else create_session_factory(engine)

    async def repositories() -> AsyncIterator[CatalogueRepository]:
        if repository is not None:
            yield repository
            return
        if session_factory is None:
            raise RuntimeError("Database session is unavailable")
        async with session_factory() as session:
            yield SqlAlchemyCatalogueRepository(session)

    async def database_ready() -> bool:
        if engine is None:
            return True
        try:
            async with engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    check_ready = readiness_check or database_ready

    @app.middleware("http")
    async def request_id(request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id_value = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        started_at = time.perf_counter()
        response = await call_next(request)
        route = request.scope.get("route")
        route_path = getattr(route, "path", "unmatched")
        if request.url.path != "/metrics":
            REQUESTS.labels(request.method, route_path, str(response.status_code)).inc()
            REQUEST_DURATION.labels(request.method, route_path).observe(time.perf_counter() - started_at)
        response.headers["X-Request-ID"] = request_id_value
        logging.getLogger("carveo.request").info(
            "request complete",
            extra={
                "request_id": request_id_value,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round((time.perf_counter() - started_at) * 1000, 2),
            },
        )
        return response

    @app.get("/metrics", include_in_schema=False)
    async def metrics() -> Response:
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

    @app.get("/health", tags=["operations"])
    async def health() -> dict[str, str]:
        return {"status": "alive"}

    @app.get("/ready", tags=["operations"], response_model=None)
    async def ready(request: Request) -> dict[str, str] | JSONResponse:
        if not await check_ready():
            return problem(
                status=503,
                slug="database-unavailable",
                title="Database unavailable",
                detail="The catalogue database is not ready.",
                instance=request.url.path,
            )
        return {"status": "ready"}

    @app.get("/api/v1/me/workspace", include_in_schema=False)
    async def workspace(buyer: AuthenticatedBuyer = Depends(require_buyer)) -> dict[str, str]:
        return {"clerkUserId": buyer.clerk_user_id}

    @app.get("/api/v1/markets", response_model=list[Market], tags=["catalogue"])
    async def markets() -> list[Market]:
        return [Market(code="ae", locale="en-ae", name="United Arab Emirates", currency="AED")]

    @app.get("/api/v1/listings", response_model=ListingPage, tags=["catalogue"])
    async def listings(
        query: ListingQuery = Depends(listing_query), repo: CatalogueRepository = Depends(repositories)
    ) -> ListingPage:
        return await repo.search(query)

    @app.get("/api/v1/listings/{listing_id}", response_model=Listing, tags=["catalogue"])
    async def detail(
        listing_id: str, request: Request, repo: CatalogueRepository = Depends(repositories)
    ) -> Listing | JSONResponse:
        item = await repo.get_by_id(listing_id)
        if item is None:
            return problem(
                status=404,
                slug="not-found",
                title="Listing not found",
                detail="The requested listing does not exist or is no longer active.",
                instance=request.url.path,
            )
        return item

    @app.get("/api/v1/listings/{listing_id}/related", response_model=list[Listing], tags=["catalogue"])
    async def related(
        listing_id: str, limit: int = Query(default=4, ge=1, le=12), repo: CatalogueRepository = Depends(repositories)
    ) -> list[Listing]:
        return await repo.get_related(listing_id, limit)

    @app.post("/api/v1/compare", response_model=CompareResponse, tags=["catalogue"])
    async def compare(payload: CompareRequest, repo: CatalogueRepository = Depends(repositories)) -> CompareResponse:
        return await repo.compare(payload)

    @app.get("/api/v1/models/{make}/{model}/insights", response_model=ModelInsights, tags=["catalogue"])
    async def insights(
        make: str, model: str, request: Request, repo: CatalogueRepository = Depends(repositories)
    ) -> ModelInsights | JSONResponse:
        result = await repo.get_model_insights(make, model)
        if result is None:
            return problem(
                status=404,
                slug="not-found",
                title="Model not found",
                detail="No active listings match this model.",
                instance=request.url.path,
            )
        return result

    return app


app = create_app()
