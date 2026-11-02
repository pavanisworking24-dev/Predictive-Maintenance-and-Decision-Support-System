import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from app.api.health import router as health_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging

setup_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Backend application starting")

    yield

    logger.info("Backend application shutting down")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

register_exception_handlers(app)


app.include_router(health_router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()

    try:
        response = await call_next(request)

        duration = time.perf_counter() - start_time

        logger.info(
            "%s %s - Status: %s - Duration: %.4f seconds",
            request.method,
            request.url.path,
            response.status_code,
            duration,
        )

        return response

    except Exception:
        logger.exception("Request failed: %s %s", request.method, request.url.path)
        raise


@app.get("/", tags=["Root"])
def root():
    return {"message": "Predictive Maintenance Backend is running"}
