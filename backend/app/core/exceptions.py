"""Domain exceptions and FastAPI handlers.

Goal: never let a raw stack trace leak to the API consumer.
Every uncaught exception turns into a structured JSON response
with a stable `code` field for the frontend to branch on.
"""
import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base class for all application-level errors."""

    code: str = "app_error"
    status_code: int = 500

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class NotFoundError(AppError):
    code = "not_found"
    status_code = 404


class ExternalAPIError(AppError):
    """Failure when calling Work24 / OpenAI etc."""

    code = "external_api_error"
    status_code = 502


class ValidationFailed(AppError):
    code = "validation_failed"
    status_code = 422


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        logger.warning(
            "app error: %s",
            exc.message,
            extra={"ctx": {"code": exc.code, "details": exc.details}},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.code, "message": exc.message, "details": exc.details},
        )

    @app.exception_handler(Exception)
    async def _unhandled(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled exception: %s", exc)
        return JSONResponse(
            status_code=500,
            content={
                "code": "internal_error",
                "message": "Internal server error",
                "details": {},
            },
        )
