"""
Validators for document uploads and operations.

This module provides validation functions for file uploads,
ensuring files meet security and business requirements.
"""
import os
import mimetypes
from typing import Tuple
from django.conf import settings
from apps.common.exceptions import ValidationError


def validate_file_size(file_size: int) -> None:
    """
    Validate file size is within acceptable limits.
    
    Args:
        file_size: Size of the file in bytes
        
    Raises:
        ValidationError: If file size exceeds limit
    """
    max_size = settings.MAX_UPLOAD_SIZE
    if file_size > max_size:
        max_size_mb = max_size / (1024 * 1024)
        raise ValidationError(
            f"File size exceeds maximum allowed size of {max_size_mb}MB"
        )
    
    if file_size <= 0:
        raise ValidationError("File is empty")


def validate_file_extension(filename: str, allowed_extensions: list) -> str:
    """
    Validate file extension is allowed.
    
    Args:
        filename: Name of the file
        allowed_extensions: List of allowed extensions
        
    Returns:
        File extension (lowercase)
        
    Raises:
        ValidationError: If extension is not allowed
    """
    extension = os.path.splitext(filename)[1].lower().lstrip('.')
    
    if not extension:
        raise ValidationError("File has no extension")
    
    if extension not in allowed_extensions:
        raise ValidationError(
            f"File extension '.{extension}' is not allowed. "
            f"Allowed extensions: {', '.join(allowed_extensions)}"
        )
    
    return extension


def validate_image_file(filename: str, file_size: int) -> str:
    """
    Validate image file for editor role.
    
    Args:
        filename: Name of the file
        file_size: Size of the file in bytes
        
    Returns:
        File extension
        
    Raises:
        ValidationError: If validation fails
    """
    validate_file_size(file_size)
    extension = validate_file_extension(
        filename,
        settings.ALLOWED_IMAGE_EXTENSIONS
    )
    return extension


def validate_document_file(filename: str, file_size: int) -> str:
    """
    Validate any document file.
    
    Args:
        filename: Name of the file
        file_size: Size of the file in bytes
        
    Returns:
        File extension
        
    Raises:
        ValidationError: If validation fails
    """
    validate_file_size(file_size)
    extension = validate_file_extension(
        filename,
        settings.ALLOWED_DOCUMENT_EXTENSIONS
    )
    return extension


def get_file_mime_type(filename: str) -> str:
    """
    Get MIME type for a file based on extension.
    
    Args:
        filename: Name of the file
        
    Returns:
        MIME type string
    """
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or 'application/octet-stream'


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing dangerous characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove path components
    filename = os.path.basename(filename)
    
    # Replace unsafe characters
    unsafe_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    
    return filename


def validate_and_prepare_file(
    filename: str,
    file_size: int,
    is_editor: bool
) -> Tuple[str, str, str]:
    """
    Validate and prepare file for upload.
    
    Args:
        filename: Original filename
        file_size: File size in bytes
        is_editor: Whether the uploader is an editor (restricted to images)
        
    Returns:
        Tuple of (sanitized_filename, extension, mime_type)
        
    Raises:
        ValidationError: If validation fails
    """
    # Sanitize filename
    clean_filename = sanitize_filename(filename)
    
    # Validate based on user role
    if is_editor:
        extension = validate_image_file(clean_filename, file_size)
    else:
        extension = validate_document_file(clean_filename, file_size)
    
    # Get MIME type
    mime_type = get_file_mime_type(clean_filename)
    
    return clean_filename, extension, mime_type

