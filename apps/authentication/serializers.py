"""
Serializers for authentication and user management.

This module defines serializers for user-related data validation
and transformation for API requests and responses.
"""
from rest_framework import serializers
from apps.authentication.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    
    Provides full user information for admin users.
    """
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserCreateSerializer(serializers.Serializer):
    """
    Serializer for creating new users.
    
    Validates user creation data including password requirements.
    """
    
    username = serializers.CharField(min_length=3, max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    role = serializers.ChoiceField(
        choices=User.Role.choices,
        default=User.Role.VIEWER
    )
    
    def validate_username(self, value):
        """Validate username format."""
        if not value.isalnum() and '_' not in value:
            raise serializers.ValidationError(
                "Username can only contain letters, numbers, and underscores"
            )
        return value


class UserUpdateRoleSerializer(serializers.Serializer):
    """Serializer for updating user roles."""
    
    role = serializers.ChoiceField(choices=User.Role.choices)


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    
    Validates login credentials.
    """
    
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change.
    
    Validates current and new passwords.
    """
    
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(min_length=8, write_only=True)
    
    def validate_new_password(self, value):
        """Ensure new password is different from current."""
        current = self.initial_data.get('current_password')
        if current and current == value:
            raise serializers.ValidationError(
                "New password must be different from current password"
            )
        return value


class TokenResponseSerializer(serializers.Serializer):
    """Serializer for token response."""
    
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()

