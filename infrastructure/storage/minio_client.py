"""
MinIO client for object storage operations.

This module provides a clean interface for interacting with MinIO object storage,
handling document upload, download, deletion, and secure URL generation.
"""
from typing import Optional, BinaryIO
from datetime import timedelta
from minio import Minio
from minio.error import S3Error
from django.conf import settings
from apps.common.exceptions import StorageError
import logging

logger = logging.getLogger(__name__)


class MinIOClient:
    """
    Client for MinIO object storage operations.
    
    This class provides methods for managing documents in MinIO storage,
    following the Single Responsibility Principle by focusing solely on
    storage operations.
    
    Attributes:
        client: MinIO client instance
        bucket_name: Name of the storage bucket
    """
    
    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        secure: bool = False,
        bucket_name: str = 'documents'
    ):
        """
        Initialize the MinIO client.
        
        Args:
            endpoint: MinIO server endpoint (host:port)
            access_key: Access key for authentication
            secret_key: Secret key for authentication
            secure: Whether to use HTTPS
            bucket_name: Name of the bucket to use
        """
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )
        self.bucket_name = bucket_name
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self) -> None:
        """
        Ensure the bucket exists, create if it doesn't.
        
        Raises:
            StorageError: If bucket creation fails
        """
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Failed to ensure bucket exists: {str(e)}")
            raise StorageError(f"Failed to create bucket: {str(e)}")
    
    def upload_file(
        self,
        file_path: str,
        file_data: BinaryIO,
        content_type: str,
        file_size: int
    ) -> str:
        """
        Upload a file to MinIO storage.
        
        Args:
            file_path: Path/name for the file in storage
            file_data: Binary file data
            content_type: MIME type of the file
            file_size: Size of the file in bytes
            
        Returns:
            The file path in storage
            
        Raises:
            StorageError: If upload fails
        """
        try:
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=file_path,
                data=file_data,
                length=file_size,
                content_type=content_type
            )
            logger.info(f"Uploaded file: {file_path}")
            return file_path
        except S3Error as e:
            logger.error(f"Failed to upload file {file_path}: {str(e)}")
            raise StorageError(f"Failed to upload file: {str(e)}")
    
    def download_file(self, file_path: str) -> bytes:
        """
        Download a file from MinIO storage.
        
        Args:
            file_path: Path of the file in storage
            
        Returns:
            File data as bytes
            
        Raises:
            StorageError: If download fails
        """
        try:
            response = self.client.get_object(
                bucket_name=self.bucket_name,
                object_name=file_path
            )
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            logger.error(f"Failed to download file {file_path}: {str(e)}")
            raise StorageError(f"Failed to download file: {str(e)}")
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from MinIO storage.
        
        Args:
            file_path: Path of the file to delete
            
        Returns:
            True if deleted successfully
            
        Raises:
            StorageError: If deletion fails
        """
        try:
            self.client.remove_object(
                bucket_name=self.bucket_name,
                object_name=file_path
            )
            logger.info(f"Deleted file: {file_path}")
            return True
        except S3Error as e:
            logger.error(f"Failed to delete file {file_path}: {str(e)}")
            raise StorageError(f"Failed to delete file: {str(e)}")
    
    def generate_presigned_url(
        self,
        file_path: str,
        expiration: Optional[timedelta] = None
    ) -> str:
        """
        Generate a secure presigned URL for temporary file access.
        
        Args:
            file_path: Path of the file in storage
            expiration: URL expiration duration (default from settings)
            
        Returns:
            Presigned URL string
            
        Raises:
            StorageError: If URL generation fails
        """
        if expiration is None:
            expiration = settings.DOCUMENT_URL_EXPIRATION
        
        try:
            url = self.client.presigned_get_object(
                bucket_name=self.bucket_name,
                object_name=file_path,
                expires=expiration
            )
            logger.debug(f"Generated presigned URL for: {file_path}")
            return url
        except S3Error as e:
            logger.error(f"Failed to generate URL for {file_path}: {str(e)}")
            raise StorageError(f"Failed to generate download URL: {str(e)}")
    
    def file_exists(self, file_path: str) -> bool:
        """
        Check if a file exists in storage.
        
        Args:
            file_path: Path of the file to check
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            self.client.stat_object(
                bucket_name=self.bucket_name,
                object_name=file_path
            )
            return True
        except S3Error:
            return False
    
    def get_file_info(self, file_path: str) -> dict:
        """
        Get metadata information about a file.
        
        Args:
            file_path: Path of the file
            
        Returns:
            Dictionary containing file metadata
            
        Raises:
            StorageError: If file doesn't exist or operation fails
        """
        try:
            stat = self.client.stat_object(
                bucket_name=self.bucket_name,
                object_name=file_path
            )
            return {
                'size': stat.size,
                'content_type': stat.content_type,
                'last_modified': stat.last_modified,
                'etag': stat.etag
            }
        except S3Error as e:
            logger.error(f"Failed to get file info for {file_path}: {str(e)}")
            raise StorageError(f"Failed to get file information: {str(e)}")


# Singleton instance
_minio_client: Optional[MinIOClient] = None


def get_minio_client() -> MinIOClient:
    """
    Get or create the MinIO client singleton instance.
    
    Returns:
        MinIOClient instance configured from Django settings
    """
    global _minio_client
    if _minio_client is None:
        _minio_client = MinIOClient(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
            bucket_name=settings.MINIO_BUCKET_NAME
        )
    return _minio_client

