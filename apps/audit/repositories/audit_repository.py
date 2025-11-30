"""
Repository for AuditLog model data access operations.

This module implements the repository pattern for AuditLog model,
providing clean data access abstractions for audit logging.
"""
from typing import Optional
from django.db.models import QuerySet
from datetime import datetime
from apps.common.repositories import BaseRepository
from apps.audit.models import AuditLog
from apps.authentication.models import User


class AuditRepository(BaseRepository[AuditLog]):
    """
    Repository for AuditLog model operations.
    
    Provides methods for creating and querying audit logs.
    """
    
    def __init__(self):
        """Initialize repository with AuditLog model."""
        super().__init__(AuditLog)
    
    def create_log(
        self,
        action: str,
        resource_type: str,
        user: Optional[User] = None,
        resource_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[dict] = None
    ) -> AuditLog:
        """
        Create an audit log entry.
        
        Args:
            action: Action type
            resource_type: Type of resource
            user: User who performed the action
            resource_id: ID of affected resource
            ip_address: Request IP address
            user_agent: Browser user agent
            details: Additional context
            
        Returns:
            Created AuditLog instance
        """
        return self.create(
            user=user,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent or '',
            details=details or {}
        )
    
    def get_user_logs(self, user: User) -> QuerySet[AuditLog]:
        """
        Get all audit logs for a specific user.
        
        Args:
            user: User instance
            
        Returns:
            QuerySet of audit logs
        """
        return self.filter(user=user)
    
    def get_document_logs(self, document_id: int) -> QuerySet[AuditLog]:
        """
        Get all audit logs for a specific document.
        
        Args:
            document_id: Document ID
            
        Returns:
            QuerySet of audit logs
        """
        return self.filter(
            resource_type=AuditLog.ResourceType.DOCUMENT,
            resource_id=document_id
        )
    
    def get_logs_by_action(self, action: str) -> QuerySet[AuditLog]:
        """
        Get audit logs by action type.
        
        Args:
            action: Action type
            
        Returns:
            QuerySet of audit logs
        """
        return self.filter(action=action)
    
    def get_logs_in_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> QuerySet[AuditLog]:
        """
        Get audit logs within a date range.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            QuerySet of audit logs
        """
        return self.filter(
            timestamp__gte=start_date,
            timestamp__lte=end_date
        )
    
    def filter_logs(
        self,
        user: Optional[User] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> QuerySet[AuditLog]:
        """
        Filter audit logs by multiple criteria.
        
        Args:
            user: Filter by user
            action: Filter by action type
            resource_type: Filter by resource type
            resource_id: Filter by resource ID
            start_date: Filter from this date
            end_date: Filter until this date
            
        Returns:
            QuerySet of filtered audit logs
        """
        queryset = self.select_related('user').all()
        
        if user:
            queryset = queryset.filter(user=user)
        
        if action:
            queryset = queryset.filter(action=action)
        
        if resource_type:
            queryset = queryset.filter(resource_type=resource_type)
        
        if resource_id:
            queryset = queryset.filter(resource_id=resource_id)
        
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        
        return queryset
    
    def get_recent_logs(self, limit: int = 100) -> QuerySet[AuditLog]:
        """
        Get most recent audit logs.
        
        Args:
            limit: Maximum number of logs to return
            
        Returns:
            QuerySet of recent audit logs
        """
        return self.select_related('user').all()[:limit]

