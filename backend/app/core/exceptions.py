"""
Comprehensive error handling system for InsuraIQ
"""
from typing import Dict, Any, Optional, Union, Type
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
import traceback
import uuid
import asyncio
import functools
from datetime import datetime
from enum import Enum
from ..core.settings import settings

logger = logging.getLogger(__name__)

class ErrorCode(Enum):
    """Standardized error codes for the application"""
    # Authentication & Authorization
    AUTHENTICATION_FAILED = "AUTH_001"
    INSUFFICIENT_PERMISSIONS = "AUTH_002"
    INVALID_TOKEN = "AUTH_003"
    TOKEN_EXPIRED = "AUTH_004"
    
    # Validation Errors
    INVALID_INPUT = "VAL_001"
    MISSING_REQUIRED_FIELD = "VAL_002"
    INVALID_FILE_TYPE = "VAL_003"
    FILE_TOO_LARGE = "VAL_004"
    INVALID_EMAIL = "VAL_005"
    INVALID_PHONE = "VAL_006"
    
    # Database Errors
    RECORD_NOT_FOUND = "DB_001"
    DUPLICATE_RECORD = "DB_002"
    DATABASE_CONNECTION_ERROR = "DB_003"
    CONSTRAINT_VIOLATION = "DB_004"
    
    # File Processing Errors
    PDF_PROCESSING_ERROR = "FILE_001"
    OCR_ERROR = "FILE_002"
    FILE_CORRUPTION = "FILE_003"
    UNSUPPORTED_FORMAT = "FILE_004"
    
    # API Integration Errors
    OPENAI_API_ERROR = "API_001"
    EXTERNAL_SERVICE_ERROR = "API_002"
    RATE_LIMIT_EXCEEDED = "API_003"
    
    # Business Logic Errors
    POLICY_COMPARISON_ERROR = "BIZ_001"
    INVALID_POLICY_STATE = "BIZ_002"
    INSUFFICIENT_DATA = "BIZ_003"
    
    # System Errors
    INTERNAL_SERVER_ERROR = "SYS_001"
    SERVICE_UNAVAILABLE = "SYS_002"
    CONFIGURATION_ERROR = "SYS_003"

class InsuraIQException(Exception):
    """Base exception class for InsuraIQ application"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        self.user_message = user_message or self._get_user_friendly_message()
        self.error_id = str(uuid.uuid4())
        self.timestamp = datetime.utcnow().isoformat()
        super().__init__(self.message)
    
    def _get_user_friendly_message(self) -> str:
        """Get user-friendly error message based on error code"""
        user_messages = {
            ErrorCode.AUTHENTICATION_FAILED: "Authentication failed. Please check your credentials.",
            ErrorCode.INSUFFICIENT_PERMISSIONS: "You don't have permission to perform this action.",
            ErrorCode.INVALID_TOKEN: "Your session has expired. Please log in again.",
            ErrorCode.TOKEN_EXPIRED: "Your session has expired. Please log in again.",
            ErrorCode.INVALID_INPUT: "The provided input is invalid. Please check your data.",
            ErrorCode.MISSING_REQUIRED_FIELD: "Required information is missing. Please complete all fields.",
            ErrorCode.INVALID_FILE_TYPE: "File type not supported. Please upload a valid file.",
            ErrorCode.FILE_TOO_LARGE: "File is too large. Please upload a smaller file.",
            ErrorCode.RECORD_NOT_FOUND: "The requested item could not be found.",
            ErrorCode.DUPLICATE_RECORD: "This item already exists.",
            ErrorCode.PDF_PROCESSING_ERROR: "Failed to process the PDF file. Please try again.",
            ErrorCode.OPENAI_API_ERROR: "AI service temporarily unavailable. Please try again later.",
            ErrorCode.RATE_LIMIT_EXCEEDED: "Too many requests. Please wait a moment and try again.",
            ErrorCode.INTERNAL_SERVER_ERROR: "An internal error occurred. Please try again later.",
        }
        return user_messages.get(self.error_code, "An unexpected error occurred.")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API response"""
        return {
            "error": {
                "code": self.error_code.value,
                "message": self.user_message,
                "error_id": self.error_id,
                "timestamp": self.timestamp,
                **({"details": self.details} if settings.LOCAL_DEV else {})
            }
        }

class ValidationException(InsuraIQException):
    """Exception for validation errors"""
    
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_INPUT,
            status_code=400,
            **kwargs
        )
        if field:
            self.details["field"] = field

class AuthenticationException(InsuraIQException):
    """Exception for authentication errors"""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(
            message=message,
            error_code=ErrorCode.AUTHENTICATION_FAILED,
            status_code=401,
            **kwargs
        )

class AuthorizationException(InsuraIQException):
    """Exception for authorization errors"""
    
    def __init__(self, message: str = "Insufficient permissions", **kwargs):
        super().__init__(
            message=message,
            error_code=ErrorCode.INSUFFICIENT_PERMISSIONS,
            status_code=403,
            **kwargs
        )

class NotFoundException(InsuraIQException):
    """Exception for not found errors"""
    
    def __init__(self, resource: str, identifier: Union[str, int], **kwargs):
        message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(
            message=message,
            error_code=ErrorCode.RECORD_NOT_FOUND,
            status_code=404,
            details={"resource": resource, "identifier": str(identifier)},
            **kwargs
        )

class FileProcessingException(InsuraIQException):
    """Exception for file processing errors"""
    
    def __init__(self, message: str, filename: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code=ErrorCode.PDF_PROCESSING_ERROR,
            status_code=422,
            **kwargs
        )
        if filename:
            self.details["filename"] = filename

class ExternalServiceException(InsuraIQException):
    """Exception for external service errors"""
    
    def __init__(self, service: str, message: str, **kwargs):
        super().__init__(
            message=f"{service}: {message}",
            error_code=ErrorCode.EXTERNAL_SERVICE_ERROR,
            status_code=503,
            details={"service": service},
            **kwargs
        )

class DatabaseException(InsuraIQException):
    """Exception for database errors"""
    
    def __init__(self, message: str, operation: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code=ErrorCode.DATABASE_CONNECTION_ERROR,
            status_code=500,
            **kwargs
        )
        if operation:
            self.details["operation"] = operation

def handle_database_error(e: Exception, operation: str) -> DatabaseException:
    """Convert database errors to standard exceptions"""
    error_message = str(e)
    
    if "unique constraint" in error_message.lower():
        return DatabaseException(
            message=f"Duplicate record in {operation}",
            error_code=ErrorCode.DUPLICATE_RECORD,
            status_code=409,
            operation=operation
        )
    elif "foreign key constraint" in error_message.lower():
        return DatabaseException(
            message=f"Invalid reference in {operation}",
            error_code=ErrorCode.CONSTRAINT_VIOLATION,
            status_code=400,
            operation=operation
        )
    else:
        return DatabaseException(
            message=f"Database error in {operation}",
            operation=operation
        )

def handle_validation_error(e: RequestValidationError) -> ValidationException:
    """Convert FastAPI validation errors to standard exceptions"""
    errors = []
    for error in e.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append(f"{field}: {error['msg']}")
    
    return ValidationException(
        message="Validation failed",
        details={"validation_errors": errors}
    )

def handle_http_error(e: StarletteHTTPException) -> InsuraIQException:
    """Convert HTTP errors to standard exceptions"""
    if e.status_code == 404:
        return NotFoundException("Resource", "unknown")
    elif e.status_code == 401:
        return AuthenticationException()
    elif e.status_code == 403:
        return AuthorizationException()
    else:
        return InsuraIQException(
            message=str(e.detail),
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            status_code=e.status_code
        )

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for the application"""
    error_id = str(uuid.uuid4())
    
    # Log the full exception details
    logger.error(
        f"Unhandled exception {error_id}: {type(exc).__name__}: {str(exc)}",
        extra={
            "error_id": error_id,
            "request_url": str(request.url),
            "request_method": request.method,
            "traceback": traceback.format_exc()
        }
    )
    
    # Convert to standard exception
    if isinstance(exc, InsuraIQException):
        response_data = exc.to_dict()
        status_code = exc.status_code
    elif isinstance(exc, RequestValidationError):
        validation_exc = handle_validation_error(exc)
        response_data = validation_exc.to_dict()
        status_code = validation_exc.status_code
    elif isinstance(exc, StarletteHTTPException):
        http_exc = handle_http_error(exc)
        response_data = http_exc.to_dict()
        status_code = http_exc.status_code
    else:
        # Unknown exception - create generic error
        generic_exc = InsuraIQException(
            message="An unexpected error occurred",
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            details={"error_id": error_id}
        )
        response_data = generic_exc.to_dict()
        status_code = 500
    
    return JSONResponse(
        status_code=status_code,
        content=response_data
    )

async def insuraiq_exception_handler(request: Request, exc: InsuraIQException) -> JSONResponse:
    """Handler for InsuraIQ custom exceptions"""
    logger.warning(
        f"InsuraIQ exception {exc.error_id}: {exc.error_code.value}: {exc.message}",
        extra={
            "error_id": exc.error_id,
            "error_code": exc.error_code.value,
            "request_url": str(request.url),
            "request_method": request.method,
            "details": exc.details
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )

# Error handling decorators
def handle_exceptions(error_code: ErrorCode = ErrorCode.INTERNAL_SERVER_ERROR):
    """Decorator to automatically handle exceptions in route handlers"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except InsuraIQException:
                raise  # Re-raise our custom exceptions
            except Exception as e:
                raise InsuraIQException(
                    message=str(e),
                    error_code=error_code
                )
        return wrapper
    return decorator
