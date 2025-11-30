"""
User and authentication-related models.

This module defines the custom User model with role-based access control.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinLengthValidator


class User(AbstractUser):
    """
    Custom user model with role-based access control.
    
    Extends Django's AbstractUser to add role-based permissions
    for the Document Management System.
    
    Roles:
        - admin: Full system access (create users, assign roles, manage all documents)
        - editor: Can upload and update images only (no delete permissions)
        - viewer: Read-only access to documents
    """
    
    class Role(models.TextChoices):
        """User role choices for RBAC."""
        ADMIN = 'admin', 'Admin'
        EDITOR = 'editor', 'Editor'
        VIEWER = 'viewer', 'Viewer'
    
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.VIEWER,
        help_text="User's role determining their permissions in the system"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['username']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self) -> str:
        """String representation of the user."""
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == self.Role.ADMIN
    
    @property
    def is_editor(self) -> bool:
        """Check if user has editor role."""
        return self.role == self.Role.EDITOR
    
    @property
    def is_viewer(self) -> bool:
        """Check if user has viewer role."""
        return self.role == self.Role.VIEWER
    
    def can_upload_documents(self) -> bool:
        """Check if user can upload documents."""
        return self.role in [self.Role.ADMIN, self.Role.EDITOR]
    
    def can_delete_documents(self) -> bool:
        """Check if user can delete documents."""
        return self.role == self.Role.ADMIN
    
    def can_manage_users(self) -> bool:
        """Check if user can manage other users."""
        return self.role == self.Role.ADMIN

