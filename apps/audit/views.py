"""
Function-based API views for audit log retrieval.

This module implements audit log API endpoints using
Django REST Framework function-based views.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from django.http import HttpResponse
import csv

from apps.audit.serializers import AuditLogSerializer
from apps.audit.services import AuditService
from apps.authentication.permissions import IsAdmin
from apps.common.exceptions import PermissionDeniedError
import logging

logger = logging.getLogger(__name__)

# Initialize service
audit_service = AuditService()


@extend_schema(
    parameters=[
        OpenApiParameter(name='user_id', type=int),
        OpenApiParameter(name='action', type=str),
        OpenApiParameter(name='resource_type', type=str),
        OpenApiParameter(name='resource_id', type=int),
        OpenApiParameter(name='page', type=int),
        OpenApiParameter(name='page_size', type=int),
    ],
    responses={
        200: AuditLogSerializer(many=True),
        403: OpenApiResponse(description="Permission denied - admin only")
    },
    description="Retrieve audit logs with filtering (admin only)"
)
@api_view(['GET'])
@permission_classes([IsAdmin])
def list_audit_logs_view(request: Request) -> Response:
    """
    Retrieve audit logs with optional filtering (admin only).
    
    Query parameters:
        - user_id: Filter by user ID
        - action: Filter by action type
        - resource_type: Filter by resource type
        - resource_id: Filter by resource ID
        - page: Page number
        - page_size: Items per page
    
    Args:
        request: HTTP request
        
    Returns:
        Paginated response with audit logs
    """
    try:
        # Get filter parameters
        user_id = request.query_params.get('user_id')
        action = request.query_params.get('action')
        resource_type = request.query_params.get('resource_type')
        resource_id = request.query_params.get('resource_id')
        
        # Convert to int if provided
        user_id = int(user_id) if user_id else None
        resource_id = int(resource_id) if resource_id else None
        
        # Get audit logs
        queryset = audit_service.get_audit_logs(
            requesting_user=request.user,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id
        )
        
        # Apply pagination
        paginator = PageNumberPagination()
        paginator.page_size = request.query_params.get('page_size', 50)
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        
        # Serialize
        serializer = AuditLogSerializer(paginated_queryset, many=True)
        
        return paginator.get_paginated_response(serializer.data)
    
    except PermissionDeniedError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_403_FORBIDDEN
        )
    except Exception as e:
        logger.error(f"Error listing audit logs: {str(e)}")
        return Response(
            {'error': 'Failed to retrieve audit logs'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    parameters=[
        OpenApiParameter(name='user_id', type=int),
        OpenApiParameter(name='action', type=str),
        OpenApiParameter(name='resource_type', type=str),
    ],
    responses={
        200: OpenApiResponse(description="CSV file download"),
        403: OpenApiResponse(description="Permission denied - admin only")
    },
    description="Export audit logs to CSV (admin only)"
)
@api_view(['GET'])
@permission_classes([IsAdmin])
def export_audit_logs_view(request: Request) -> HttpResponse:
    """
    Export audit logs to CSV format (admin only).
    
    Args:
        request: HTTP request
        
    Returns:
        CSV file response
    """
    try:
        # Get filter parameters
        user_id = request.query_params.get('user_id')
        action = request.query_params.get('action')
        resource_type = request.query_params.get('resource_type')
        resource_id = request.query_params.get('resource_id')
        
        # Convert to int if provided
        user_id = int(user_id) if user_id else None
        resource_id = int(resource_id) if resource_id else None
        
        # Get audit logs
        queryset = audit_service.get_audit_logs(
            requesting_user=request.user,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id
        )
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="audit_logs.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Timestamp', 'Username', 'Action', 'Resource Type',
            'Resource ID', 'IP Address', 'User Agent'
        ])
        
        for log in queryset:
            writer.writerow([
                log.timestamp,
                log.user.username if log.user else 'System',
                log.get_action_display(),
                log.get_resource_type_display(),
                log.resource_id or '',
                log.ip_address or '',
                log.user_agent[:50] if log.user_agent else ''
            ])
        
        return response
    
    except PermissionDeniedError as e:
        return HttpResponse(
            f"Error: {str(e)}",
            status=status.HTTP_403_FORBIDDEN
        )
    except Exception as e:
        logger.error(f"Error exporting audit logs: {str(e)}")
        return HttpResponse(
            'Failed to export audit logs',
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

