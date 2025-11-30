"""
Authentication service containing business logic.

This module implements authentication-related business logic,
following the service layer pattern to separate concerns.
"""
from typing import Optional, Dict, Any
from django.contrib.auth import authenticate
from django.db import transaction
from apps.authentication.models import User
from apps.authentication.repositories import UserRepository
from apps.common.exceptions import ValidationError, AuthenticationError, PermissionDeniedError
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """
    Service class for authentication and user management operations.
    
    This class implements business logic for authentication, following
    the Single Responsibility Principle by focusing on auth-related operations.
    """
    
    def __init__(self):
        """Initialize service with repository dependency."""
        self.user_repository = UserRepository()
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user with username and password.
        
        Args:
            username: User's username
            password: User's password
            
        Returns:
            Authenticated User instance if successful, None otherwise
            
        Raises:
            AuthenticationError: If authentication fails
        """
        user = authenticate(username=username, password=password)
        
        if user is None:
            logger.warning(f"Failed authentication attempt for username: {username}")
            raise AuthenticationError("Invalid username or password")
        
        if not user.is_active:
            logger.warning(f"Inactive user login attempt: {username}")
            raise AuthenticationError("User account is disabled")
        
        logger.info(f"User authenticated successfully: {username}")
        return user
    
    @transaction.atomic
    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        role: str = User.Role.VIEWER,
        requesting_user: Optional[User] = None,
        **extra_fields
    ) -> User:
        """
        Create a new user account.
        
        Args:
            username: Username for the new user
            email: Email address
            password: Password (will be hashed)
            role: User role (default: viewer)
            requesting_user: User making the request (for permission check)
            **extra_fields: Additional user fields
            
        Returns:
            Created User instance
            
        Raises:
            PermissionDeniedError: If requesting user lacks permission
            ValidationError: If validation fails
        """
        # Check permissions
        if requesting_user and not requesting_user.can_manage_users():
            raise PermissionDeniedError("Only admins can create users")
        
        # Validate input
        self._validate_user_data(username, email, password)
        
        # Check if username or email already exists
        if self.user_repository.username_exists(username):
            raise ValidationError(f"Username '{username}' already exists")
        
        if self.user_repository.email_exists(email):
            raise ValidationError(f"Email '{email}' already exists")
        
        # Validate role
        if role not in [r.value for r in User.Role]:
            raise ValidationError(f"Invalid role: {role}")
        
        # Create user
        user = self.user_repository.create_user(
            username=username,
            email=email,
            password=password,
            role=role,
            **extra_fields
        )
        
        logger.info(f"User created: {username} with role {role}")
        return user
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User instance if found, None otherwise
        """
        return self.user_repository.get_by_id(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Username
            
        Returns:
            User instance if found, None otherwise
        """
        return self.user_repository.get_by_username(username)
    
    @transaction.atomic
    def update_user_role(
        self,
        user_id: int,
        new_role: str,
        requesting_user: User
    ) -> User:
        """
        Update a user's role.
        
        Args:
            user_id: ID of user to update
            new_role: New role value
            requesting_user: User making the request
            
        Returns:
            Updated User instance
            
        Raises:
            PermissionDeniedError: If requesting user lacks permission
            ValidationError: If validation fails
        """
        # Check permissions
        if not requesting_user.can_manage_users():
            raise PermissionDeniedError("Only admins can update user roles")
        
        # Validate role
        if new_role not in [r.value for r in User.Role]:
            raise ValidationError(f"Invalid role: {new_role}")
        
        # Get and update user
        user = self.user_repository.get_or_raise(user_id)
        user = self.user_repository.update_role(user, new_role)
        
        logger.info(f"User {user.username} role updated to {new_role} by {requesting_user.username}")
        return user
    
    @transaction.atomic
    def change_password(
        self,
        user_id: int,
        current_password: str,
        new_password: str
    ) -> User:
        """
        Change a user's password.
        
        Args:
            user_id: User ID
            current_password: Current password for verification
            new_password: New password
            
        Returns:
            Updated User instance
            
        Raises:
            AuthenticationError: If current password is incorrect
            ValidationError: If new password is invalid
        """
        user = self.user_repository.get_or_raise(user_id)
        
        # Verify current password
        if not user.check_password(current_password):
            raise AuthenticationError("Current password is incorrect")
        
        # Validate new password
        self._validate_password(new_password)
        
        # Update password
        user = self.user_repository.change_password(user, new_password)
        
        logger.info(f"Password changed for user: {user.username}")
        return user
    
    def list_users(self, requesting_user: User) -> list[User]:
        """
        List all users (admin only).
        
        Args:
            requesting_user: User making the request
            
        Returns:
            List of User instances
            
        Raises:
            PermissionDeniedError: If requesting user lacks permission
        """
        if not requesting_user.can_manage_users():
            raise PermissionDeniedError("Only admins can list users")
        
        return list(self.user_repository.get_active_users())
    
    def _validate_user_data(self, username: str, email: str, password: str) -> None:
        """
        Validate user input data.
        
        Args:
            username: Username to validate
            email: Email to validate
            password: Password to validate
            
        Raises:
            ValidationError: If validation fails
        """
        if not username or len(username) < 3:
            raise ValidationError("Username must be at least 3 characters long")
        
        if not email or '@' not in email:
            raise ValidationError("Invalid email address")
        
        self._validate_password(password)
    
    def _validate_password(self, password: str) -> None:
        """
        Validate password strength.
        
        Args:
            password: Password to validate
            
        Raises:
            ValidationError: If password doesn't meet requirements
        """
        if not password or len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long")

