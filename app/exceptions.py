from datetime import datetime, timezone
from fastapi import Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    status_code: int = 500
    message: str = "An error occurred"
    headers: dict | None = None

    def __init__(self, message: str | None = None, headers: dict | None = None):
        if message is not None:
            self.message = message
        if headers is not None:
            self.headers = headers


class NotFoundException(AppException):
    status_code = 404
    message = "Resource not found"


class UnauthorizedException(AppException):
    status_code = 401
    message = "Unauthorized"
    
    def __init__(self, message: str | None = None, headers: dict | None = None):
        super().__init__(message, headers)
        # Default OAuth2 header if not provided
        if self.headers is None:
            self.headers = {"WWW-Authenticate": "Bearer"}


class BadRequestException(AppException):
    status_code = 400
    message = "Bad request"


class ValidationException(AppException):
    status_code = 422
    message = "Validation error"


def error_body(status_code: int, detail: str, request: Request) -> dict:
    return {
        "status_code": status_code,
        "detail": detail,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "path": request.url.path,
    }


def format_error_response(status_code: int, detail: str, request: Request) -> JSONResponse:
    return JSONResponse(status_code=status_code, content=error_body(status_code, detail, request))


def register_exception_handlers(app):
    from fastapi.exceptions import RequestValidationError

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # Flatten pydantic errors to a readable message
        detail = "; ".join([f"{e['loc']}: {e['msg']}" for e in exc.errors()]) or "Validation error"
        return format_error_response(422, detail, request)

    @app.exception_handler(NotFoundException)
    async def not_found_handler(request: Request, exc: NotFoundException):
        return format_error_response(exc.status_code, exc.message, request)

    @app.exception_handler(UnauthorizedException)
    async def unauthorized_handler(request: Request, exc: UnauthorizedException):
        response = format_error_response(exc.status_code, exc.message, request)
        # Add OAuth2 headers if present
        if exc.headers:
            for key, value in exc.headers.items():
                response.headers[key] = value
        return response

    @app.exception_handler(BadRequestException)
    async def bad_request_handler(request: Request, exc: BadRequestException):
        return format_error_response(exc.status_code, exc.message, request)

    @app.exception_handler(ValidationException)
    async def custom_validation_handler(request: Request, exc: ValidationException):
        return format_error_response(exc.status_code, exc.message, request)
