"""
Tests for authentication models.
"""
import pytest
from apps.authentication.models import User


@pytest.mark.django_db
class TestUserModel:
    """Test User model."""
    
    def test_create_user(self):
        """Test creating a user."""
        user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            role=User.Role.VIEWER
        )
        
        assert user.id is not None
        assert user.username == 'testuser'
        assert user.email == 'test@test.com'
        assert user.role == User.Role.VIEWER
        assert user.check_password('testpass123')
    
    def test_user_roles(self):
        """Test user role properties."""
        admin = User.objects.create_user(
            username='admin',
            password='pass',
            role=User.Role.ADMIN
        )
        editor = User.objects.create_user(
            username='editor',
            password='pass',
            role=User.Role.EDITOR
        )
        viewer = User.objects.create_user(
            username='viewer',
            password='pass',
            role=User.Role.VIEWER
        )
        
        assert admin.is_admin is True
        assert admin.can_upload_documents() is True
        assert admin.can_delete_documents() is True
        
        assert editor.is_editor is True
        assert editor.can_upload_documents() is True
        assert editor.can_delete_documents() is False
        
        assert viewer.is_viewer is True
        assert viewer.can_upload_documents() is False
        assert viewer.can_delete_documents() is False
    
    def test_user_string_representation(self):
        """Test user __str__ method."""
        user = User.objects.create_user(
            username='testuser',
            password='pass',
            role=User.Role.ADMIN
        )
        
        assert str(user) == 'testuser (Admin)'

