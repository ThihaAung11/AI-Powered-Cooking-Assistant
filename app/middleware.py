import time
from datetime import datetime, timezone
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .exceptions import AppException, format_error_response


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response: Response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        print(f"{request.method} {request.url.path} -> {response.status_code} ({process_time:.2f} ms)")
        return response


async def error_handling_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except AppException as ex:
        # Custom exceptions already standardized
        return format_error_response(ex.status_code, ex.message, request)
    except Exception as ex:  # Unhandled exceptions
        print(f"Unhandled error: {ex}")
        return format_error_response(500, "Internal server error", request)
