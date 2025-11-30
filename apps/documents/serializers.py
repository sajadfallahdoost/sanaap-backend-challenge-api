"""
Serializers for document management.

This module defines serializers for document-related data validation
and transformation for API requests and responses.
"""
from rest_framework import serializers
from apps.documents.models import Document
from apps.authentication.serializers import UserSerializer


class DocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for Document model.
    
    Provides complete document information including uploader details.
    """
    
    uploaded_by = UserSerializer(read_only=True)
    file_size_display = serializers.SerializerMethodField()
    is_image = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'description', 'file_type', 'file_extension',
            'size', 'file_size_display', 'is_image', 'uploaded_by',
            'processing_status', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'file_type', 'file_extension', 'size',
            'uploaded_by', 'processing_status', 'created_at', 'updated_at'
        ]
    
    def get_file_size_display(self, obj):
        """Get human-readable file size."""
        return obj.get_file_size_display()


class DocumentUploadSerializer(serializers.Serializer):
    """
    Serializer for document upload.
    
    Validates file upload data.
    """
    
    file = serializers.FileField()
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)


class DocumentUpdateSerializer(serializers.Serializer):
    """
    Serializer for document update.
    
    Allows updating title, description, and optionally the file.
    """
    
    title = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    file = serializers.FileField(required=False)


class DocumentListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for document listing.
    
    Excludes heavy fields for better performance.
    """
    
    uploaded_by_username = serializers.CharField(
        source='uploaded_by.username',
        read_only=True
    )
    file_size_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'file_extension', 'file_size_display',
            'uploaded_by_username', 'processing_status', 'created_at'
        ]
    
    def get_file_size_display(self, obj):
        """Get human-readable file size."""
        from apps.documents.utils.helpers import format_file_size
        return format_file_size(obj.size)


class DocumentDownloadSerializer(serializers.Serializer):
    """
    Serializer for document download response.
    
    Returns the presigned URL for downloading.
    """
    
    download_url = serializers.URLField()
    expires_in = serializers.CharField()
    document = DocumentSerializer()

