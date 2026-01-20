from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import Any, Dict, Optional
from app.core.logging_config import logger

class AppException(Exception):
    """
    Base class for application-specific exceptions.
    """
    def __init__(self, message: str, error_type: str = "app_error", status_code: int = 400, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_type = error_type
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)

def create_error_response(
    status_code: int,
    message: str,
    error_type: str,
    details: Optional[Any] = None
) -> JSONResponse:
    """
    Creates a standardized JSON response for errors.
    """
    content = {
        "success": False,
        "error_type": error_type,
        "message": message,
    }
    if details:
        content["details"] = details
        
    return JSONResponse(
        status_code=status_code,
        content=content
    )

async def app_exception_handler(request: Request, exc: AppException):
    return create_error_response(
        status_code=exc.status_code,
        message=exc.message,
        error_type=exc.error_type,
        details=exc.details
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # Preserve `detail` key to maintain compatibility with some clients/tests
    resp = create_error_response(
        status_code=exc.status_code,
        message=exc.detail,
        error_type="http_error"
    )
    # Add a `detail` field mirroring the original Starlette detail
    try:
        body = resp.body.decode()
        # resp is a JSONResponse; update its content dict instead of re-encoding
        content = resp.body
    except Exception:
        pass
    # Patch the response content to include `detail` alongside `message`
    resp_content = resp.body
    # Since JSONResponse stores the content separately, we can set the .media attribute via json
    import json as _json
    parsed = _json.loads(resp.body)
    parsed["detail"] = exc.detail
    resp.body = _json.dumps(parsed).encode()
    return resp

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Simplify the validation errors for the client
    details = []
    for error in exc.errors():
        field = ".".join(str(e) for e in error["loc"])
        msg = error["msg"]
        details.append({"field": field, "issue": msg})
        
    return create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Request validation failed",
        error_type="validation_error",
        details=details
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    # Log the full error
    logger.error(f"Database error: {exc}", exc_info=True)
    
    if isinstance(exc, IntegrityError):
        return create_error_response(
            status_code=status.HTTP_409_CONFLICT,
            message="Data conflict: Resource already exists or violates constraints.",
            error_type="database_conflict"
        )
        
    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="A database error occurred.",
        error_type="database_error"
    )

async def general_exception_handler(request: Request, exc: Exception):
    # Log the full error
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="An unexpected error occurred. Please try again later.",
        error_type="server_error"
    )

def add_exception_handlers(app):
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
