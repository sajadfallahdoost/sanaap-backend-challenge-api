"""
Tests for authentication API views.
"""
import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestAuthenticationViews:
    """Test authentication API endpoints."""
    
    def test_login_success(self, api_client, admin_user):
        """Test successful login."""
        url = reverse('authentication:login')
        data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data
        assert response.data['user']['username'] == 'admin'
    
    def test_login_invalid_credentials(self, api_client, admin_user):
        """Test login with invalid credentials."""
        url = reverse('authentication:login')
        data = {
            'username': 'admin',
            'password': 'wrongpassword'
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user(self, authenticated_client, admin_user):
        """Test getting current user information."""
        url = reverse('authentication:current_user')
        
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'admin'
        assert response.data['role'] == 'admin'
    
    def test_get_current_user_unauthenticated(self, api_client):
        """Test getting current user without authentication."""
        url = reverse('authentication:current_user')
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_user_as_admin(self, authenticated_client):
        """Test creating user as admin."""
        url = reverse('authentication:create_user')
        data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'password123',
            'role': 'editor'
        }
        
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['username'] == 'newuser'
        assert response.data['role'] == 'editor'
    
    def test_create_user_as_viewer(self, api_client, viewer_user):
        """Test creating user as viewer (should fail)."""
        api_client.force_authenticate(user=viewer_user)
        url = reverse('authentication:create_user')
        data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'password123',
            'role': 'editor'
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_list_users_as_admin(self, authenticated_client, editor_user, viewer_user):
        """Test listing users as admin."""
        url = reverse('authentication:list_users')
        
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 3  # admin, editor, viewer
    
    def test_change_password(self, api_client, admin_user):
        """Test password change."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('authentication:change_password')
        data = {
            'current_password': 'admin123',
            'new_password': 'newpassword123'
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data

