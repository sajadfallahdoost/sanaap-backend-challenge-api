"""
Audit logging models.

This module defines models for tracking user actions,
document access, and system changes for compliance and security.
"""
from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    """
    Audit log model for tracking system actions.
    
    Records all significant actions performed in the system including
    document access, modifications, user management, and authentication events.
    
    Attributes:
        user: User who performed the action (nullable for system actions)
        action: Type of action performed
        resource_type: Type of resource affected
        resource_id: ID of the affected resource
        ip_address: IP address of the request
        user_agent: Browser user agent string
        details: JSON field with additional context
        timestamp: When the action occurred
    """
    
    class Action(models.TextChoices):
        """Action types for audit logging."""
        # Authentication actions
        LOGIN = 'login', 'User Login'
        LOGOUT = 'logout', 'User Logout'
        LOGIN_FAILED = 'login_failed', 'Failed Login Attempt'
        
        # Document actions
        DOCUMENT_UPLOAD = 'document_upload', 'Document Uploaded'
        DOCUMENT_VIEW = 'document_view', 'Document Viewed'
        DOCUMENT_DOWNLOAD = 'document_download', 'Document Downloaded'
        DOCUMENT_UPDATE = 'document_update', 'Document Updated'
        DOCUMENT_DELETE = 'document_delete', 'Document Deleted'
        
        # User management actions
        USER_CREATE = 'user_create', 'User Created'
        USER_UPDATE = 'user_update', 'User Updated'
        USER_ROLE_CHANGE = 'user_role_change', 'User Role Changed'
        USER_DELETE = 'user_delete', 'User Deleted'
        PASSWORD_CHANGE = 'password_change', 'Password Changed'
        
        # System actions
        SYSTEM_ERROR = 'system_error', 'System Error'
    
    class ResourceType(models.TextChoices):
        """Resource types that can be audited."""
        USER = 'user', 'User'
        DOCUMENT = 'document', 'Document'
        SYSTEM = 'system', 'System'
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        help_text="User who performed the action"
    )
    action = models.CharField(
        max_length=50,
        choices=Action.choices,
        help_text="Type of action performed"
    )
    resource_type = models.CharField(
        max_length=20,
        choices=ResourceType.choices,
        help_text="Type of resource affected"
    )
    resource_id = models.IntegerField(
        null=True,
        blank=True,
        help_text="ID of the affected resource"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the request"
    )
    user_agent = models.TextField(
        blank=True,
        help_text="Browser user agent string"
    )
    details = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional context and details"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When the action occurred"
    )
    
    class Meta:
        db_table = 'audit_logs'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['action']),
            models.Index(fields=['resource_type', 'resource_id']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self) -> str:
        """String representation of the audit log."""
        user_str = self.user.username if self.user else 'System'
        return f"{user_str} - {self.get_action_display()} - {self.timestamp}"
    
    @property
    def action_display(self) -> str:
        """Get human-readable action name."""
        return self.get_action_display()

