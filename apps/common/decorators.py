"""
Custom decorators for views and functions.

This module provides reusable decorators for common functionality
like transaction management and permission checking.
"""
from functools import wraps
from typing import Callable, Any
from django.db import transaction
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from apps.common.exceptions import PermissionDeniedError
import logging

logger = logging.getLogger(__name__)


def atomic_transaction(func: Callable) -> Callable:
    """
    Decorator to wrap a function in a database transaction.
    
    If the function raises an exception, all database operations are rolled back.
    
    Args:
        func: The function to wrap
        
    Returns:
        Wrapped function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        with transaction.atomic():
            return func(*args, **kwargs)
    return wrapper


def require_role(*allowed_roles: str) -> Callable:
    """
    Decorator to enforce role-based access control for function-based views.
    
    Args:
        *allowed_roles: Roles that are allowed to access this view
        
    Returns:
        Decorator function
        
    Example:
        @require_role('admin', 'editor')
        def my_view(request):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(request: Request, *args, **kwargs) -> Response:
            if not hasattr(request, 'user') or not request.user.is_authenticated:
                raise PermissionDeniedError("Authentication required")
            
            user_role = getattr(request.user, 'role', None)
            if user_role not in allowed_roles:
                logger.warning(
                    f"Access denied for user {request.user.id} with role {user_role}. "
                    f"Required roles: {allowed_roles}"
                )
                raise PermissionDeniedError(
                    f"Access denied. Required role(s): {', '.join(allowed_roles)}"
                )
            
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def log_execution(func: Callable) -> Callable:
    """
    Decorator to log function execution for debugging and monitoring.
    
    Args:
        func: The function to wrap
        
    Returns:
        Wrapped function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Executing {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed with error: {str(e)}")
            raise
    return wrapper

