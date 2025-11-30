"""
Helper functions for document operations.

This module provides utility functions for generating file paths,
creating unique identifiers, and other document-related operations.
"""
import os
import uuid
from datetime import datetime
from typing import Optional


def generate_unique_filename(original_filename: str) -> str:
    """
    Generate a unique filename to prevent collisions.
    
    Args:
        original_filename: Original filename with extension
        
    Returns:
        Unique filename with UUID and timestamp
    """
    name, extension = os.path.splitext(original_filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = uuid.uuid4().hex[:8]
    return f"{name}_{timestamp}_{unique_id}{extension}"


def generate_file_path(user_id: int, filename: str) -> str:
    """
    Generate storage path for a file.
    
    Files are organized by user ID and upload date for better organization.
    
    Args:
        user_id: ID of the user uploading the file
        filename: Filename
        
    Returns:
        Full storage path
    """
    date_path = datetime.now().strftime('%Y/%m/%d')
    unique_filename = generate_unique_filename(filename)
    return f"users/{user_id}/{date_path}/{unique_filename}"


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def extract_file_info(file_path: str) -> dict:
    """
    Extract information from a file path.
    
    Args:
        file_path: Storage file path
        
    Returns:
        Dictionary with path components
    """
    parts = file_path.split('/')
    return {
        'filename': parts[-1] if parts else '',
        'directory': '/'.join(parts[:-1]) if len(parts) > 1 else '',
        'user_folder': parts[1] if len(parts) > 1 else '',
    }

