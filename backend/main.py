"""FastAPI entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging

configure_logging()

import logging
from app.routers import jobs, match, portfolio, programs, qualifications

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
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
