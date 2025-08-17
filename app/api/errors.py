#app/api/errors.py

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette import status


class AppError(Exception):
    code = "internal_error"
    http_status = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message: str = "Internal server error", details=None):
        super().__init__(message)
        self.message = message
        self.details = details


class NotFoundError(AppError):
    code = "not_found"
    http_status = status.HTTP_404_NOT_FOUND


class UnauthorizedError(AppError):
    code = "unauthorized"
    http_status = status.HTTP_401_UNAUTHORIZED


class ValidationAppError(AppError):
    code = "validation_error"
    http_status = status.HTTP_422_UNPROCESSABLE_ENTITY


def install_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.http_status,
            content={"code": exc.code, "message": exc.message, "details": exc.details},
        )
