"""
Custom permission classes for DRF views.

This module defines role-based permission classes used by Django REST Framework
to control access to API endpoints.
"""
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView
from apps.authentication.models import User


class IsAdmin(permissions.BasePermission):
    """
    Permission class allowing only admin users.
    
    Admins have full system access including user management
    and all document operations.
    """
    
    message = "Only administrators can perform this action."
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Check if user is authenticated and has admin role.
        
        Args:
            request: The request object
            view: The view being accessed
            
        Returns:
            True if user is admin, False otherwise
        """
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == User.Role.ADMIN
        )


class IsEditor(permissions.BasePermission):
    """
    Permission class allowing editor and admin users.
    
    Editors can upload and update images but cannot delete documents.
    """
    
    message = "Only editors or administrators can perform this action."
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Check if user is authenticated and has editor or admin role.
        
        Args:
            request: The request object
            view: The view being accessed
            
        Returns:
            True if user is editor or admin, False otherwise
        """
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in [User.Role.EDITOR, User.Role.ADMIN]
        )


class IsViewer(permissions.BasePermission):
    """
    Permission class allowing all authenticated users.
    
    Viewers can only read documents, not create or modify them.
    """
    
    message = "Authentication required."
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Check if user is authenticated.
        
        Args:
            request: The request object
            view: The view being accessed
            
        Returns:
            True if user is authenticated, False otherwise
        """
        return request.user and request.user.is_authenticated


class CanUploadDocuments(permissions.BasePermission):
    """
    Permission class for document upload operations.
    
    Only admins and editors can upload documents.
    """
    
    message = "You don't have permission to upload documents."
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Check if user can upload documents.
        
        Args:
            request: The request object
            view: The view being accessed
            
        Returns:
            True if user can upload, False otherwise
        """
        return (
            request.user and
            request.user.is_authenticated and
            request.user.can_upload_documents()
        )


class CanDeleteDocuments(permissions.BasePermission):
    """
    Permission class for document deletion.
    
    Only admins can delete documents.
    """
    
    message = "Only administrators can delete documents."
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Check if user can delete documents.
        
        Args:
            request: The request object
            view: The view being accessed
            
        Returns:
            True if user can delete, False otherwise
        """
        return (
            request.user and
            request.user.is_authenticated and
            request.user.can_delete_documents()
        )

