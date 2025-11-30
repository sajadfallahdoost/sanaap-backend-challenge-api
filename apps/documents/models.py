"""
Document models for the DMS application.

This module defines the Document model for storing document metadata
and tracking document processing status.
"""
from django.db import models
from django.conf import settings
from apps.authentication.models import User


class Document(models.Model):
    """
    Document model for storing document metadata.
    
    The actual file is stored in MinIO, while this model stores
    metadata and references to the file.
    
    Attributes:
        title: Document title/name
        description: Optional document description
        file_path: Path to the file in MinIO storage
        file_type: MIME type of the file
        file_extension: File extension (jpg, png, pdf, etc.)
        size: File size in bytes
        uploaded_by: User who uploaded the document
        processing_status: Status of background processing
        created_at: Timestamp when document was created
        updated_at: Timestamp when document was last updated
    """
    
    class ProcessingStatus(models.TextChoices):
        """Document processing status choices."""
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
    
    title = models.CharField(
        max_length=255,
        help_text="Document title or filename"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional document description"
    )
    file_path = models.CharField(
        max_length=500,
        unique=True,
        help_text="Path to the file in object storage"
    )
    file_type = models.CharField(
        max_length=100,
        help_text="MIME type of the file"
    )
    file_extension = models.CharField(
        max_length=10,
        help_text="File extension"
    )
    size = models.BigIntegerField(
        help_text="File size in bytes"
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='documents',
        help_text="User who uploaded this document"
    )
    processing_status = models.CharField(
        max_length=20,
        choices=ProcessingStatus.choices,
        default=ProcessingStatus.PENDING,
        help_text="Background processing status"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'documents'
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['uploaded_by']),
            models.Index(fields=['file_type']),
            models.Index(fields=['file_extension']),
            models.Index(fields=['processing_status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self) -> str:
        """String representation of the document."""
        return f"{self.title} ({self.file_extension})"
    
    @property
    def is_image(self) -> bool:
        """Check if the document is an image file."""
        return self.file_extension.lower() in settings.ALLOWED_IMAGE_EXTENSIONS
    
    @property
    def is_processing_complete(self) -> bool:
        """Check if background processing is complete."""
        return self.processing_status == self.ProcessingStatus.COMPLETED
    
    def get_file_size_display(self) -> str:
        """Get human-readable file size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.size < 1024.0:
                return f"{self.size:.2f} {unit}"
            self.size /= 1024.0
        return f"{self.size:.2f} TB"

