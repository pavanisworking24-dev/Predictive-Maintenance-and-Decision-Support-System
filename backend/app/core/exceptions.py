import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI):

    # Handle HTTP errors such as 404, 401 and 403.
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        error_codes = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            409: "CONFLICT",
            503: "SERVICE_UNAVAILABLE",
        }

        error_code = error_codes.get(exc.status_code, "HTTP_ERROR")

        message = (
            exc.detail if isinstance(exc.detail, str) else "The request could not be processed"
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={"error": error_code, "message": message, "details": None},
            headers=exc.headers,
        )

    # Handle invalid request data.
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        issues = []

        for error in exc.errors():
            issues.append(
                {
                    "field": ".".join(str(item) for item in error["loc"]),
                    "message": error["msg"],
                    "type": error["type"],
                }
            )

        return JSONResponse(
            status_code=422,
            content={
                "error": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": {"issues": issues},
            },
        )

    # Handle unexpected server errors.
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.exception("Unexpected application error")

        return JSONResponse(
            status_code=500,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred",
                "details": None,
            },
        )
