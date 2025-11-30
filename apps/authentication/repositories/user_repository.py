"""
Repository for User model data access operations.

This module implements the repository pattern for User model,
providing a clean abstraction over database operations.
"""
from typing import Optional, List
from django.db.models import QuerySet
from apps.common.repositories import BaseRepository
from apps.authentication.models import User


class UserRepository(BaseRepository[User]):
    """
    Repository for User model operations.
    
    Provides methods for user data access following the repository pattern,
    ensuring separation of data access logic from business logic.
    """
    
    def __init__(self):
        """Initialize repository with User model."""
        super().__init__(User)
    
    def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: The username to search for
            
        Returns:
            User instance if found, None otherwise
        """
        try:
            return self.model.objects.get(username=username)
        except User.DoesNotExist:
            return None
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: The email to search for
            
        Returns:
            User instance if found, None otherwise
        """
        try:
            return self.model.objects.get(email=email)
        except User.DoesNotExist:
            return None
    
    def get_users_by_role(self, role: str) -> QuerySet[User]:
        """
        Get all users with a specific role.
        
        Args:
            role: The role to filter by
            
        Returns:
            QuerySet of users with the specified role
        """
        return self.filter(role=role)
    
    def get_active_users(self) -> QuerySet[User]:
        """
        Get all active users.
        
        Returns:
            QuerySet of active users
        """
        return self.filter(is_active=True)
    
    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        role: str = User.Role.VIEWER,
        **extra_fields
    ) -> User:
        """
        Create a new user with encrypted password.
        
        Args:
            username: Username for the new user
            email: Email address
            password: Plain text password (will be hashed)
            role: User role (default: viewer)
            **extra_fields: Additional user fields
            
        Returns:
            Created User instance
        """
        user = self.model(
            username=username,
            email=email,
            role=role,
            **extra_fields
        )
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(
        self,
        username: str,
        email: str,
        password: str,
        **extra_fields
    ) -> User:
        """
        Create a superuser with admin role.
        
        Args:
            username: Username for the superuser
            email: Email address
            password: Plain text password (will be hashed)
            **extra_fields: Additional user fields
            
        Returns:
            Created superuser instance
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.ADMIN)
        
        return self.create_user(username, email, password, **extra_fields)
    
    def update_role(self, user: User, new_role: str) -> User:
        """
        Update a user's role.
        
        Args:
            user: User instance to update
            new_role: New role value
            
        Returns:
            Updated user instance
        """
        return self.update(user, role=new_role)
    
    def change_password(self, user: User, new_password: str) -> User:
        """
        Change a user's password.
        
        Args:
            user: User instance
            new_password: New plain text password (will be hashed)
            
        Returns:
            Updated user instance
        """
        user.set_password(new_password)
        user.save()
        return user
    
    def username_exists(self, username: str) -> bool:
        """
        Check if a username already exists.
        
        Args:
            username: Username to check
            
        Returns:
            True if exists, False otherwise
        """
        return self.exists(username=username)
    
    def email_exists(self, email: str) -> bool:
        """
        Check if an email already exists.
        
        Args:
            email: Email to check
            
        Returns:
            True if exists, False otherwise
        """
        return self.exists(email=email)

