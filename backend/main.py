"""FastAPI entry point."""
import subprocess
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging

configure_logging()

from app.routers import jobs, match, portfolio, programs, qualifications

logger = logging.getLogger(__name__)


def _run_migrations() -> None:
    """앱 시작 시 alembic 마이그레이션 자동 실행."""
    try:
        logger.info("running alembic migrations...")
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            logger.info("migrations completed successfully")
        else:
            logger.error("migration failed: %s", result.stderr)
    except Exception as e:
        logger.error("migration error: %s", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    _run_migrations()
    logger.info("careermatch starting", extra={"ctx": {"env": settings.environment}})
    yield
    logger.info("careermatch shutting down")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="CareerMatch API", version="2.0.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)
    app.include_router(portfolio.router,      prefix="/api/portfolio",      tags=["portfolio"])
    app.include_router(programs.router,       prefix="/api/programs",       tags=["programs"])
    app.include_router(match.router,          prefix="/api/match",          tags=["match"])
    app.include_router(qualifications.router, prefix="/api/qualifications", tags=["qualifications"])
    app.include_router(jobs.router,           prefix="/api/jobs",           tags=["jobs"])

    @app.get("/", tags=["meta"])
    def root() -> dict:
        return {"service": "careermatch", "version": "2.0.0", "docs": "/docs"}

    @app.get("/health", tags=["meta"])
    def health() -> dict:
        return {"status": "healthy"}

    return app


app = create_app()
