"""
Function-based API views for document management.

This module implements all document-related API endpoints
using Django REST Framework function-based views.
"""
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from django.conf import settings

from apps.documents.serializers import (
    DocumentSerializer,
    DocumentUploadSerializer,
    DocumentUpdateSerializer,
    DocumentListSerializer,
    DocumentDownloadSerializer
)
from apps.documents.services import DocumentService
from apps.documents.filters import DocumentFilter
from apps.authentication.permissions import (
    CanUploadDocuments,
    CanDeleteDocuments
)
from apps.common.exceptions import (
    ValidationError,
    PermissionDeniedError,
    NotFoundError,
    StorageError
)
import logging

logger = logging.getLogger(__name__)

# Initialize service
document_service = DocumentService()


@extend_schema(
    request=DocumentUploadSerializer,
    responses={
        201: DocumentSerializer,
        400: OpenApiResponse(description="Validation error"),
        403: OpenApiResponse(description="Permission denied")
    },
    description="Upload a new document"
)
@api_view(['POST'])
@permission_classes([CanUploadDocuments])
@parser_classes([MultiPartParser, FormParser])
def upload_document_view(request: Request) -> Response:
    """
    Upload a new document.
    
    Editors can only upload image files.
    Admins can upload any supported file type.
    
    Args:
        request: HTTP request with file and metadata
        
    Returns:
        Response with created document data
    """
    serializer = DocumentUploadSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    try:
        document = document_service.upload_document(
            file=serializer.validated_data['file'],
            title=serializer.validated_data['title'],
            description=serializer.validated_data.get('description', ''),
            user=request.user
        )
        
        return Response(
            DocumentSerializer(document).data,
            status=status.HTTP_201_CREATED
        )
    
    except (ValidationError, StorageError) as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except PermissionDeniedError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_403_FORBIDDEN
        )


@extend_schema(
    parameters=[
        OpenApiParameter(name='document_id', type=int, location=OpenApiParameter.PATH)
    ],
    responses={
        200: DocumentSerializer,
        404: OpenApiResponse(description="Document not found")
    },
    description="Get document details"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_document_view(request: Request, document_id: int) -> Response:
    """
    Get document details by ID.
    
    Args:
        request: HTTP request
        document_id: Document ID
        
    Returns:
        Response with document data
    """
    try:
        document = document_service.get_document(
            document_id=document_id,
            user=request.user
        )
        
        return Response(
            DocumentSerializer(document).data,
            status=status.HTTP_200_OK
        )
    
    except NotFoundError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_404_NOT_FOUND
        )


@extend_schema(
    parameters=[
        OpenApiParameter(name='document_id', type=int, location=OpenApiParameter.PATH)
    ],
    responses={
        200: DocumentDownloadSerializer,
        404: OpenApiResponse(description="Document not found")
    },
    description="Generate a secure download URL for a document"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_document_view(request: Request, document_id: int) -> Response:
    """
    Generate a secure presigned URL for downloading a document.
    
    Args:
        request: HTTP request
        document_id: Document ID
        
    Returns:
        Response with download URL
    """
    try:
        document = document_service.get_document(document_id, request.user)
        download_url = document_service.generate_download_url(
            document_id=document_id,
            user=request.user
        )
        
        expiration_hours = settings.DOCUMENT_URL_EXPIRATION.total_seconds() / 3600
        
        return Response({
            'download_url': download_url,
            'expires_in': f"{expiration_hours} hours",
            'document': DocumentSerializer(document).data
        }, status=status.HTTP_200_OK)
    
    except NotFoundError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_404_NOT_FOUND
        )
    except StorageError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    parameters=[
        OpenApiParameter(name='document_id', type=int, location=OpenApiParameter.PATH)
    ],
    request=DocumentUpdateSerializer,
    responses={
        200: DocumentSerializer,
        400: OpenApiResponse(description="Validation error"),
        403: OpenApiResponse(description="Permission denied"),
        404: OpenApiResponse(description="Document not found")
    },
    description="Update document metadata or file"
)
@api_view(['PUT', 'PATCH'])
@permission_classes([CanUploadDocuments])
@parser_classes([MultiPartParser, FormParser])
def update_document_view(request: Request, document_id: int) -> Response:
    """
    Update a document's metadata or replace the file.
    
    Editors can only update their own documents.
    Admins can update any document.
    
    Args:
        request: HTTP request with update data
        document_id: Document ID
        
    Returns:
        Response with updated document data
    """
    serializer = DocumentUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    try:
        document = document_service.update_document(
            document_id=document_id,
            user=request.user,
            title=serializer.validated_data.get('title'),
            description=serializer.validated_data.get('description'),
            file=serializer.validated_data.get('file')
        )
        
        return Response(
            DocumentSerializer(document).data,
            status=status.HTTP_200_OK
        )
    
    except NotFoundError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_404_NOT_FOUND
        )
    except (ValidationError, StorageError) as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except PermissionDeniedError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_403_FORBIDDEN
        )


@extend_schema(
    parameters=[
        OpenApiParameter(name='document_id', type=int, location=OpenApiParameter.PATH)
    ],
    responses={
        204: OpenApiResponse(description="Document deleted successfully"),
        403: OpenApiResponse(description="Permission denied - admin only"),
        404: OpenApiResponse(description="Document not found")
    },
    description="Delete a document (admin only)"
)
@api_view(['DELETE'])
@permission_classes([CanDeleteDocuments])
def delete_document_view(request: Request, document_id: int) -> Response:
    """
    Delete a document (admin only).
    
    Args:
        request: HTTP request
        document_id: Document ID
        
    Returns:
        Response confirming deletion
    """
    try:
        document_service.delete_document(
            document_id=document_id,
            user=request.user
        )
        
        return Response(
            {'message': 'Document deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )
    
    except NotFoundError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_404_NOT_FOUND
        )
    except PermissionDeniedError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_403_FORBIDDEN
        )
    except StorageError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    parameters=[
        OpenApiParameter(name='file_type', type=str),
        OpenApiParameter(name='file_extension', type=str),
        OpenApiParameter(name='search', type=str),
        OpenApiParameter(name='page', type=int),
        OpenApiParameter(name='page_size', type=int),
    ],
    responses={
        200: DocumentListSerializer(many=True),
    },
    description="List documents with filtering and pagination"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_documents_view(request: Request) -> Response:
    """
    List documents with optional filtering and pagination.
    
    Viewers and editors see only their own documents.
    Admins see all documents.
    
    Query parameters:
        - file_type: Filter by MIME type
        - file_extension: Filter by file extension
        - search: Search in title and description
        - page: Page number
        - page_size: Items per page
    
    Args:
        request: HTTP request
        
    Returns:
        Paginated response with document list
    """
    try:
        # Get filter parameters
        file_type = request.query_params.get('file_type')
        file_extension = request.query_params.get('file_extension')
        search_query = request.query_params.get('search')
        
        # Get documents queryset
        queryset = document_service.list_documents(
            user=request.user,
            file_type=file_type,
            file_extension=file_extension,
            search_query=search_query
        )
        
        # Apply pagination
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        paginator.page_size = request.query_params.get('page_size', 20)
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        
        # Serialize
        serializer = DocumentListSerializer(paginated_queryset, many=True)
        
        return paginator.get_paginated_response(serializer.data)
    
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        return Response(
            {'error': 'Failed to list documents'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

