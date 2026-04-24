"""Structured JSON logging.

A single `configure_logging()` call wires Python's stdlib logging
to emit JSON lines, keeping uvicorn access logs in the same format
so downstream log shippers (CloudWatch, Loki, etc.) can parse them.
"""
import json
import logging
import sys
from logging.config import dictConfig

from app.core.config import get_settings


class JsonFormatter(logging.Formatter):
    """Minimal JSON formatter without external dependencies."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        # Allow callers to attach structured context via `extra={"ctx": {...}}`
        ctx = getattr(record, "ctx", None)
        if isinstance(ctx, dict):
            payload["ctx"] = ctx
        return json.dumps(payload, ensure_ascii=False)


def configure_logging() -> None:
    settings = get_settings()
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {"()": "app.core.logging.JsonFormatter"},
            },
            "handlers": {
                "stdout": {
                    "class": "logging.StreamHandler",
                    "stream": sys.stdout,
                    "formatter": "json",
                },
            },
            "root": {
                "level": settings.log_level,
                "handlers": ["stdout"],
            },
            "loggers": {
                "uvicorn": {"level": settings.log_level, "propagate": True, "handlers": []},
                "uvicorn.access": {"level": settings.log_level, "propagate": True, "handlers": []},
                "uvicorn.error": {"level": settings.log_level, "propagate": True, "handlers": []},
            },
        }
    )
