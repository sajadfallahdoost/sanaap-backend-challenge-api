"""
Pytest fixtures for authentication tests.
"""
import pytest
from rest_framework.test import APIClient
from apps.authentication.models import User


@pytest.fixture
def api_client():
    """Provide API client for testing."""
    return APIClient()


@pytest.fixture
def admin_user(db):
    """Create an admin user for testing."""
    return User.objects.create_user(
        username='admin',
        email='admin@test.com',
        password='admin123',
        role=User.Role.ADMIN,
        is_staff=True
    )


@pytest.fixture
def editor_user(db):
    """Create an editor user for testing."""
    return User.objects.create_user(
        username='editor',
        email='editor@test.com',
        password='editor123',
        role=User.Role.EDITOR
    )


@pytest.fixture
def viewer_user(db):
    """Create a viewer user for testing."""
    return User.objects.create_user(
        username='viewer',
        email='viewer@test.com',
        password='viewer123',
        role=User.Role.VIEWER
    )


@pytest.fixture
def authenticated_client(api_client, admin_user):
    """Provide authenticated API client."""
    api_client.force_authenticate(user=admin_user)
    return api_client

