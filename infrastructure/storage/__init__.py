"""
Storage services for document management.
"""
from .minio_client import MinIOClient, get_minio_client

__all__ = ['MinIOClient', 'get_minio_client']

