"""
URL patterns for authentication endpoints.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'authentication'

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', views.current_user_view, name='current_user'),
    path('change-password/', views.change_password_view, name='change_password'),
    
    # User Management (Admin only)
    path('users/', views.list_users_view, name='list_users'),
    path('users/create/', views.create_user_view, name='create_user'),
    path('users/<int:user_id>/', views.get_user_view, name='get_user'),
    path('users/<int:user_id>/role/', views.update_user_role_view, name='update_role'),
]

