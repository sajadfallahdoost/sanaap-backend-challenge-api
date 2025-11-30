"""
Function-based API views for authentication and user management.

This module implements all authentication-related API endpoints
using Django REST Framework function-based views.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from apps.authentication.serializers import (
    UserSerializer,
    UserCreateSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
    UserUpdateRoleSerializer,
    TokenResponseSerializer
)
from apps.authentication.services import AuthService
from apps.authentication.permissions import IsAdmin
from apps.common.decorators import require_role
from apps.common.exceptions import ValidationError, AuthenticationError
import logging

logger = logging.getLogger(__name__)

# Initialize service
auth_service = AuthService()


def get_tokens_for_user(user):
    """
    Generate JWT tokens for a user.
    
    Args:
        user: User instance
        
    Returns:
        Dictionary with access and refresh tokens
    """
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@extend_schema(
    request=LoginSerializer,
    responses={
        200: TokenResponseSerializer,
        401: OpenApiResponse(description="Invalid credentials")
    },
    description="Authenticate user and return JWT tokens"
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request: Request) -> Response:
    """
    Authenticate user and return JWT tokens.
    
    Args:
        request: HTTP request with username and password
        
    Returns:
        Response with access token, refresh token, and user data
    """
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    try:
        user = auth_service.authenticate_user(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        
        tokens = get_tokens_for_user(user)
        
        return Response({
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
    
    except AuthenticationError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_401_UNAUTHORIZED
        )


@extend_schema(
    responses={
        200: UserSerializer,
        401: OpenApiResponse(description="Not authenticated")
    },
    description="Get current authenticated user information"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request: Request) -> Response:
    """
    Get current authenticated user information.
    
    Args:
        request: HTTP request
        
    Returns:
        Response with current user data
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    request=UserCreateSerializer,
    responses={
        201: UserSerializer,
        400: OpenApiResponse(description="Validation error"),
        403: OpenApiResponse(description="Permission denied")
    },
    description="Create a new user (admin only)"
)
@api_view(['POST'])
@permission_classes([IsAdmin])
def create_user_view(request: Request) -> Response:
    """
    Create a new user (admin only).
    
    Args:
        request: HTTP request with user data
        
    Returns:
        Response with created user data
    """
    serializer = UserCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    try:
        user = auth_service.create_user(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            role=serializer.validated_data.get('role', 'viewer'),
            first_name=serializer.validated_data.get('first_name', ''),
            last_name=serializer.validated_data.get('last_name', ''),
            requesting_user=request.user
        )
        
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )
    
    except ValidationError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(
    responses={
        200: UserSerializer(many=True),
        403: OpenApiResponse(description="Permission denied")
    },
    description="List all users (admin only)"
)
@api_view(['GET'])
@permission_classes([IsAdmin])
def list_users_view(request: Request) -> Response:
    """
    List all users (admin only).
    
    Args:
        request: HTTP request
        
    Returns:
        Response with list of users
    """
    users = auth_service.list_users(requesting_user=request.user)
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    parameters=[
        OpenApiParameter(name='user_id', type=int, location=OpenApiParameter.PATH)
    ],
    responses={
        200: UserSerializer,
        404: OpenApiResponse(description="User not found")
    },
    description="Get user details by ID (admin only)"
)
@api_view(['GET'])
@permission_classes([IsAdmin])
def get_user_view(request: Request, user_id: int) -> Response:
    """
    Get user details by ID (admin only).
    
    Args:
        request: HTTP request
        user_id: ID of the user to retrieve
        
    Returns:
        Response with user data
    """
    user = auth_service.get_user_by_id(user_id)
    
    if not user:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    parameters=[
        OpenApiParameter(name='user_id', type=int, location=OpenApiParameter.PATH)
    ],
    request=UserUpdateRoleSerializer,
    responses={
        200: UserSerializer,
        400: OpenApiResponse(description="Validation error"),
        403: OpenApiResponse(description="Permission denied"),
        404: OpenApiResponse(description="User not found")
    },
    description="Update user role (admin only)"
)
@api_view(['PATCH'])
@permission_classes([IsAdmin])
def update_user_role_view(request: Request, user_id: int) -> Response:
    """
    Update user role (admin only).
    
    Args:
        request: HTTP request with new role
        user_id: ID of the user to update
        
    Returns:
        Response with updated user data
    """
    serializer = UserUpdateRoleSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    try:
        user = auth_service.update_user_role(
            user_id=user_id,
            new_role=serializer.validated_data['role'],
            requesting_user=request.user
        )
        
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_200_OK
        )
    
    except ValidationError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(
    request=ChangePasswordSerializer,
    responses={
        200: OpenApiResponse(description="Password changed successfully"),
        400: OpenApiResponse(description="Validation error"),
        401: OpenApiResponse(description="Current password incorrect")
    },
    description="Change current user's password"
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request: Request) -> Response:
    """
    Change current user's password.
    
    Args:
        request: HTTP request with current and new password
        
    Returns:
        Response confirming password change
    """
    serializer = ChangePasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    try:
        auth_service.change_password(
            user_id=request.user.id,
            current_password=serializer.validated_data['current_password'],
            new_password=serializer.validated_data['new_password']
        )
        
        return Response(
            {'message': 'Password changed successfully'},
            status=status.HTTP_200_OK
        )
    
    except (AuthenticationError, ValidationError) as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

