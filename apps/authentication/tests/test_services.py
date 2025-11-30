"""
Tests for authentication services.
"""
import pytest
from apps.authentication.services import AuthService
from apps.authentication.models import User
from apps.common.exceptions import (
    ValidationError,
    AuthenticationError,
    PermissionDeniedError
)


@pytest.mark.django_db
class TestAuthService:
    """Test AuthService business logic."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = AuthService()
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='admin123',
            role=User.Role.ADMIN
        )
    
    def test_authenticate_user_success(self):
        """Test successful user authentication."""
        user = self.service.authenticate_user('admin', 'admin123')
        
        assert user is not None
        assert user.username == 'admin'
    
    def test_authenticate_user_wrong_password(self):
        """Test authentication with wrong password."""
        with pytest.raises(AuthenticationError):
            self.service.authenticate_user('admin', 'wrongpass')
    
    def test_authenticate_user_nonexistent(self):
        """Test authentication with nonexistent user."""
        with pytest.raises(AuthenticationError):
            self.service.authenticate_user('nobody', 'pass')
    
    def test_create_user_success(self):
        """Test successful user creation."""
        user = self.service.create_user(
            username='newuser',
            email='new@test.com',
            password='password123',
            role=User.Role.EDITOR,
            requesting_user=self.admin
        )
        
        assert user.id is not None
        assert user.username == 'newuser'
        assert user.email == 'new@test.com'
        assert user.role == User.Role.EDITOR
    
    def test_create_user_duplicate_username(self):
        """Test creating user with duplicate username."""
        with pytest.raises(ValidationError) as exc:
            self.service.create_user(
                username='admin',  # Already exists
                email='new@test.com',
                password='password123',
                requesting_user=self.admin
            )
        
        assert 'already exists' in str(exc.value).lower()
    
    def test_create_user_invalid_email(self):
        """Test creating user with invalid email."""
        with pytest.raises(ValidationError):
            self.service.create_user(
                username='newuser',
                email='invalidemail',  # No @
                password='password123',
                requesting_user=self.admin
            )
    
    def test_create_user_short_password(self):
        """Test creating user with short password."""
        with pytest.raises(ValidationError):
            self.service.create_user(
                username='newuser',
                email='new@test.com',
                password='short',  # Too short
                requesting_user=self.admin
            )
    
    def test_create_user_permission_denied(self):
        """Test creating user without admin permission."""
        viewer = User.objects.create_user(
            username='viewer',
            password='pass',
            role=User.Role.VIEWER
        )
        
        with pytest.raises(PermissionDeniedError):
            self.service.create_user(
                username='newuser',
                email='new@test.com',
                password='password123',
                requesting_user=viewer
            )
    
    def test_update_user_role(self):
        """Test updating user role."""
        user = User.objects.create_user(
            username='user',
            password='pass',
            role=User.Role.VIEWER
        )
        
        updated = self.service.update_user_role(
            user_id=user.id,
            new_role=User.Role.EDITOR,
            requesting_user=self.admin
        )
        
        assert updated.role == User.Role.EDITOR
    
    def test_change_password_success(self):
        """Test successful password change."""
        user = self.service.change_password(
            user_id=self.admin.id,
            current_password='admin123',
            new_password='newpassword123'
        )
        
        assert user.check_password('newpassword123')
    
    def test_change_password_wrong_current(self):
        """Test password change with wrong current password."""
        with pytest.raises(AuthenticationError):
            self.service.change_password(
                user_id=self.admin.id,
                current_password='wrongpass',
                new_password='newpassword123'
            )

