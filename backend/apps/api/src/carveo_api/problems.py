from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def problem(*, status: int, slug: str, title: str, detail: str, instance: str, errors: Any = None) -> JSONResponse:
    body: dict[str, Any] = {
        "type": f"https://carveo.local/problems/{slug}",
        "title": title,
        "status": status,
        "detail": detail,
        "instance": instance,
    }
    if errors is not None:
        body["errors"] = errors
    return JSONResponse(body, status_code=status, media_type="application/problem+json")


async def validation_problem(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = [
        {"location": list(error["loc"]), "message": error["msg"], "type": error["type"]} for error in exc.errors()
    ]
    return problem(
        status=422,
        slug="validation",
        title="Request validation failed",
        detail="One or more request values are invalid.",
        instance=str(request.url.path),
        errors=errors,
    )
