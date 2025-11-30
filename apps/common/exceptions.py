"""
Custom exception classes and exception handler for the DMS application.

This module provides standardized error handling across the entire application,
ensuring consistent error responses for API clients.
"""
from typing import Any, Dict, Optional
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


class DMSException(Exception):
    """
    Base exception class for all DMS custom exceptions.
    
    All custom exceptions should inherit from this class to maintain
    a consistent exception hierarchy.
    """
    
    default_message = "An error occurred"
    default_code = "error"
    status_code = status.HTTP_400_BAD_REQUEST
    
    def __init__(self, message: Optional[str] = None, code: Optional[str] = None):
        """
        Initialize the exception.
        
        Args:
            message: Custom error message
            code: Error code for client identification
        """
        self.message = message or self.default_message
        self.code = code or self.default_code
        super().__init__(self.message)


class ValidationError(DMSException):
    """Raised when validation fails."""
    default_message = "Validation error"
    default_code = "validation_error"
    status_code = status.HTTP_400_BAD_REQUEST


class PermissionDeniedError(DMSException):
    """Raised when user lacks required permissions."""
    default_message = "Permission denied"
    default_code = "permission_denied"
    status_code = status.HTTP_403_FORBIDDEN


class NotFoundError(DMSException):
    """Raised when a requested resource is not found."""
    default_message = "Resource not found"
    default_code = "not_found"
    status_code = status.HTTP_404_NOT_FOUND


class StorageError(DMSException):
    """Raised when storage operations fail."""
    default_message = "Storage operation failed"
    default_code = "storage_error"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class AuthenticationError(DMSException):
    """Raised when authentication fails."""
    default_message = "Authentication failed"
    default_code = "authentication_error"
    status_code = status.HTTP_401_UNAUTHORIZED


def custom_exception_handler(exc: Exception, context: Dict[str, Any]) -> Optional[Response]:
    """
    Custom exception handler for DRF views.
    
    This handler provides consistent error responses and logs exceptions
    for monitoring and debugging.
    
    Args:
        exc: The exception that was raised
        context: Context information about the request
        
    Returns:
        Response object with error details
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # Handle custom DMS exceptions
    if isinstance(exc, DMSException):
        logger.warning(
            f"DMS Exception: {exc.code} - {exc.message}",
            extra={'exception': exc, 'context': context}
        )
        return Response(
            {
                'error': {
                    'code': exc.code,
                    'message': exc.message,
                }
            },
            status=exc.status_code
        )
    
    # Log unhandled exceptions
    if response is None:
        logger.error(
            f"Unhandled exception: {str(exc)}",
            exc_info=True,
            extra={'context': context}
        )
        return Response(
            {
                'error': {
                    'code': 'server_error',
                    'message': 'An unexpected error occurred',
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return response

