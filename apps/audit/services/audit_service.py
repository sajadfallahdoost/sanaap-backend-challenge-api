"""
Audit service containing business logic for logging.

This module implements audit logging business logic,
providing methods to log various system actions.
"""
from typing import Optional
from django.http import HttpRequest
from apps.audit.models import AuditLog
from apps.audit.repositories import AuditRepository
from apps.authentication.models import User
from apps.common.exceptions import PermissionDeniedError
import logging

logger = logging.getLogger(__name__)


class AuditService:
    """
    Service class for audit logging operations.
    
    Provides methods to log various actions and retrieve audit logs.
    """
    
    def __init__(self):
        """Initialize service with repository dependency."""
        self.repository = AuditRepository()
    
    def _get_client_ip(self, request: Optional[HttpRequest]) -> Optional[str]:
        """
        Extract client IP address from request.
        
        Args:
            request: HTTP request object
            
        Returns:
            IP address string or None
        """
        if not request:
            return None
        
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _get_user_agent(self, request: Optional[HttpRequest]) -> str:
        """
        Extract user agent from request.
        
        Args:
            request: HTTP request object
            
        Returns:
            User agent string
        """
        if not request:
            return ''
        return request.META.get('HTTP_USER_AGENT', '')
    
    def log_document_upload(
        self,
        user: User,
        document_id: int,
        request: Optional[HttpRequest] = None,
        details: Optional[dict] = None
    ) -> AuditLog:
        """
        Log document upload action.
        
        Args:
            user: User who uploaded the document
            document_id: ID of uploaded document
            request: HTTP request object
            details: Additional context
            
        Returns:
            Created AuditLog instance
        """
        return self.repository.create_log(
            action=AuditLog.Action.DOCUMENT_UPLOAD,
            resource_type=AuditLog.ResourceType.DOCUMENT,
            user=user,
            resource_id=document_id,
            ip_address=self._get_client_ip(request),
            user_agent=self._get_user_agent(request),
            details=details or {}
        )
    
    def log_document_access(
        self,
        user: User,
        document_id: int,
        action: str,
        request: Optional[HttpRequest] = None,
        details: Optional[dict] = None
    ) -> AuditLog:
        """
        Log document access (view/download).
        
        Args:
            user: User accessing the document
            document_id: ID of accessed document
            action: Specific action (view or download)
            request: HTTP request object
            details: Additional context
            
        Returns:
            Created AuditLog instance
        """
        audit_action = {
            'view': AuditLog.Action.DOCUMENT_VIEW,
            'download': AuditLog.Action.DOCUMENT_DOWNLOAD
        }.get(action, AuditLog.Action.DOCUMENT_VIEW)
        
        return self.repository.create_log(
            action=audit_action,
            resource_type=AuditLog.ResourceType.DOCUMENT,
            user=user,
            resource_id=document_id,
            ip_address=self._get_client_ip(request),
            user_agent=self._get_user_agent(request),
            details=details or {}
        )
    
    def log_document_change(
        self,
        user: User,
        document_id: int,
        action: str,
        request: Optional[HttpRequest] = None,
        details: Optional[dict] = None
    ) -> AuditLog:
        """
        Log document modification (update/delete).
        
        Args:
            user: User modifying the document
            document_id: ID of modified document
            action: Specific action (update or delete)
            request: HTTP request object
            details: Additional context
            
        Returns:
            Created AuditLog instance
        """
        audit_action = {
            'update': AuditLog.Action.DOCUMENT_UPDATE,
            'delete': AuditLog.Action.DOCUMENT_DELETE
        }.get(action, AuditLog.Action.DOCUMENT_UPDATE)
        
        return self.repository.create_log(
            action=audit_action,
            resource_type=AuditLog.ResourceType.DOCUMENT,
            user=user,
            resource_id=document_id,
            ip_address=self._get_client_ip(request),
            user_agent=self._get_user_agent(request),
            details=details or {}
        )
    
    def log_user_action(
        self,
        user: User,
        action: str,
        target_user_id: Optional[int] = None,
        request: Optional[HttpRequest] = None,
        details: Optional[dict] = None
    ) -> AuditLog:
        """
        Log user management action.
        
        Args:
            user: User performing the action
            action: Action type (create, update, role_change, delete)
            target_user_id: ID of the user being modified
            request: HTTP request object
            details: Additional context
            
        Returns:
            Created AuditLog instance
        """
        action_map = {
            'create': AuditLog.Action.USER_CREATE,
            'update': AuditLog.Action.USER_UPDATE,
            'role_change': AuditLog.Action.USER_ROLE_CHANGE,
            'delete': AuditLog.Action.USER_DELETE,
            'password_change': AuditLog.Action.PASSWORD_CHANGE
        }
        
        audit_action = action_map.get(action, AuditLog.Action.USER_UPDATE)
        
        return self.repository.create_log(
            action=audit_action,
            resource_type=AuditLog.ResourceType.USER,
            user=user,
            resource_id=target_user_id,
            ip_address=self._get_client_ip(request),
            user_agent=self._get_user_agent(request),
            details=details or {}
        )
    
    def log_authentication(
        self,
        action: str,
        user: Optional[User] = None,
        request: Optional[HttpRequest] = None,
        details: Optional[dict] = None
    ) -> AuditLog:
        """
        Log authentication event (login/logout/failed).
        
        Args:
            action: Action type (login, logout, login_failed)
            user: User involved in the action
            request: HTTP request object
            details: Additional context
            
        Returns:
            Created AuditLog instance
        """
        action_map = {
            'login': AuditLog.Action.LOGIN,
            'logout': AuditLog.Action.LOGOUT,
            'login_failed': AuditLog.Action.LOGIN_FAILED
        }
        
        audit_action = action_map.get(action, AuditLog.Action.LOGIN)
        
        return self.repository.create_log(
            action=audit_action,
            resource_type=AuditLog.ResourceType.SYSTEM,
            user=user,
            ip_address=self._get_client_ip(request),
            user_agent=self._get_user_agent(request),
            details=details or {}
        )
    
    def get_audit_logs(
        self,
        requesting_user: User,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None
    ):
        """
        Retrieve audit logs with filtering (admin only).
        
        Args:
            requesting_user: User making the request
            user_id: Filter by user ID
            action: Filter by action type
            resource_type: Filter by resource type
            resource_id: Filter by resource ID
            
        Returns:
            QuerySet of audit logs
            
        Raises:
            PermissionDeniedError: If user is not admin
        """
        if not requesting_user.is_admin:
            raise PermissionDeniedError(
                "Only administrators can access audit logs"
            )
        
        user = None
        if user_id:
            from apps.authentication.repositories import UserRepository
            user_repo = UserRepository()
            user = user_repo.get_by_id(user_id)
        
        return self.repository.filter_logs(
            user=user,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id
        )

