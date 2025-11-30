"""
Document service containing business logic.

This module implements document-related business logic,
following the service layer pattern to separate concerns.
"""
from typing import Optional, BinaryIO
from django.db import transaction
from django.conf import settings
from apps.documents.models import Document
from apps.documents.repositories import DocumentRepository
from apps.documents.utils.validators import validate_and_prepare_file
from apps.documents.utils.helpers import generate_file_path
from apps.authentication.models import User
from apps.common.exceptions import (
    ValidationError,
    PermissionDeniedError,
    NotFoundError,
    StorageError
)
from infrastructure.storage import get_minio_client
from apps.documents.services.notification_service import get_notification_service
import logging

logger = logging.getLogger(__name__)


class DocumentService:
    """
    Service class for document management operations.
    
    This class implements business logic for documents, following
    the Single Responsibility Principle by focusing on document operations.
    
    Attributes:
        repository: Document repository for data access
        storage_client: MinIO client for file storage
    """
    
    def __init__(self):
        """Initialize service with dependencies."""
        self.repository = DocumentRepository()
        self.storage_client = get_minio_client()
        self.notification_service = get_notification_service()
    
    @transaction.atomic
    def upload_document(
        self,
        file,
        title: str,
        user: User,
        description: str = ""
    ) -> Document:
        """
        Upload a new document.
        
        Args:
            file: Uploaded file object
            title: Document title
            user: User uploading the document
            description: Optional document description
            
        Returns:
            Created Document instance
            
        Raises:
            PermissionDeniedError: If user lacks upload permission
            ValidationError: If validation fails
            StorageError: If storage operation fails
        """
        # Check permissions
        if not user.can_upload_documents():
            raise PermissionDeniedError(
                "You don't have permission to upload documents"
            )
        
        # Get file info
        filename = file.name
        file_size = file.size
        
        # Validate file
        is_editor = user.is_editor
        clean_filename, extension, mime_type = validate_and_prepare_file(
            filename,
            file_size,
            is_editor
        )
        
        # Generate storage path
        file_path = generate_file_path(user.id, clean_filename)
        
        try:
            # Upload to MinIO
            file.seek(0)  # Reset file pointer
            self.storage_client.upload_file(
                file_path=file_path,
                file_data=file,
                content_type=mime_type,
                file_size=file_size
            )
            
            # Create database record
            document = self.repository.create(
                title=title,
                description=description,
                file_path=file_path,
                file_type=mime_type,
                file_extension=extension,
                size=file_size,
                uploaded_by=user,
                processing_status=Document.ProcessingStatus.PENDING
            )
            
            logger.info(
                f"Document uploaded: {document.id} by user {user.username}"
            )
            
            # Send real-time notification
            self.notification_service.notify_document_created(document, user)
            
            return document
        
        except StorageError as e:
            logger.error(f"Failed to upload document to storage: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during upload: {str(e)}")
            # Attempt to clean up uploaded file if database save fails
            try:
                if self.storage_client.file_exists(file_path):
                    self.storage_client.delete_file(file_path)
            except:
                pass
            raise StorageError(f"Failed to upload document: {str(e)}")
    
    def get_document(self, document_id: int, user: User) -> Document:
        """
        Get a document by ID.
        
        Args:
            document_id: Document ID
            user: Requesting user
            
        Returns:
            Document instance
            
        Raises:
            NotFoundError: If document doesn't exist
        """
        document = self.repository.get_by_id_with_user(document_id)
        
        if not document:
            raise NotFoundError(f"Document with ID {document_id} not found")
        
        return document
    
    def generate_download_url(
        self,
        document_id: int,
        user: User
    ) -> str:
        """
        Generate a secure temporary download URL for a document.
        
        Args:
            document_id: Document ID
            user: Requesting user
            
        Returns:
            Presigned URL for downloading
            
        Raises:
            NotFoundError: If document doesn't exist
            StorageError: If URL generation fails
        """
        document = self.get_document(document_id, user)
        
        try:
            url = self.storage_client.generate_presigned_url(
                file_path=document.file_path,
                expiration=settings.DOCUMENT_URL_EXPIRATION
            )
            
            logger.debug(
                f"Generated download URL for document {document_id} "
                f"for user {user.username}"
            )
            
            return url
        
        except StorageError as e:
            logger.error(
                f"Failed to generate URL for document {document_id}: {str(e)}"
            )
            raise
    
    @transaction.atomic
    def update_document(
        self,
        document_id: int,
        user: User,
        title: Optional[str] = None,
        description: Optional[str] = None,
        file = None
    ) -> Document:
        """
        Update a document's metadata or file.
        
        Args:
            document_id: Document ID
            user: User making the update
            title: New title (optional)
            description: New description (optional)
            file: New file to replace existing (optional)
            
        Returns:
            Updated Document instance
            
        Raises:
            NotFoundError: If document doesn't exist
            PermissionDeniedError: If user lacks permission
            ValidationError: If validation fails
        """
        document = self.get_document(document_id, user)
        
        # Check permissions - editors can update, admins can update all
        if not user.can_upload_documents():
            raise PermissionDeniedError(
                "You don't have permission to update documents"
            )
        
        # Editors can only update their own documents
        if user.is_editor and document.uploaded_by != user:
            raise PermissionDeniedError(
                "You can only update your own documents"
            )
        
        update_data = {}
        
        if title is not None:
            update_data['title'] = title
        
        if description is not None:
            update_data['description'] = description
        
        # If file is being replaced
        if file:
            filename = file.name
            file_size = file.size
            
            # Validate new file
            is_editor = user.is_editor
            clean_filename, extension, mime_type = validate_and_prepare_file(
                filename,
                file_size,
                is_editor
            )
            
            # Generate new path
            new_file_path = generate_file_path(user.id, clean_filename)
            
            try:
                # Upload new file
                file.seek(0)
                self.storage_client.upload_file(
                    file_path=new_file_path,
                    file_data=file,
                    content_type=mime_type,
                    file_size=file_size
                )
                
                # Delete old file
                try:
                    self.storage_client.delete_file(document.file_path)
                except:
                    logger.warning(
                        f"Failed to delete old file: {document.file_path}"
                    )
                
                # Update file info
                update_data.update({
                    'file_path': new_file_path,
                    'file_type': mime_type,
                    'file_extension': extension,
                    'size': file_size,
                    'processing_status': Document.ProcessingStatus.PENDING
                })
            
            except StorageError as e:
                logger.error(f"Failed to update document file: {str(e)}")
                raise
        
        if update_data:
            document = self.repository.update(document, **update_data)
            logger.info(
                f"Document {document_id} updated by user {user.username}"
            )
            
            # Send real-time notification
            self.notification_service.notify_document_updated(document, user)
        
        return document
    
    @transaction.atomic
    def delete_document(self, document_id: int, user: User) -> None:
        """
        Delete a document (admin only).
        
        Args:
            document_id: Document ID
            user: User requesting deletion
            
        Raises:
            NotFoundError: If document doesn't exist
            PermissionDeniedError: If user is not admin
            StorageError: If storage deletion fails
        """
        if not user.can_delete_documents():
            raise PermissionDeniedError(
                "Only administrators can delete documents"
            )
        
        document = self.get_document(document_id, user)
        
        try:
            # Delete from storage
            self.storage_client.delete_file(document.file_path)
            
            # Delete from database
            self.repository.delete(document)
            
            logger.info(
                f"Document {document_id} deleted by admin {user.username}"
            )
        
        except StorageError as e:
            logger.error(
                f"Failed to delete document {document_id} from storage: {str(e)}"
            )
            raise
    
    def list_documents(
        self,
        user: User,
        file_type: Optional[str] = None,
        file_extension: Optional[str] = None,
        search_query: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ):
        """
        List documents with optional filtering.
        
        Args:
            user: Requesting user
            file_type: Filter by MIME type
            file_extension: Filter by extension
            search_query: Search in title and description
            start_date: Filter by start date
            end_date: Filter by end date
            
        Returns:
            QuerySet of documents
        """
        # Editors and viewers see only their own documents, admins see all
        uploaded_by = None if user.is_admin else user
        
        return self.repository.filter_documents(
            file_type=file_type,
            file_extension=file_extension,
            uploaded_by=uploaded_by,
            search_query=search_query
        )
    
    def update_processing_status(
        self,
        document_id: int,
        status: str
    ) -> Document:
        """
        Update document processing status (for background tasks).
        
        Args:
            document_id: Document ID
            status: New processing status
            
        Returns:
            Updated document
            
        Raises:
            NotFoundError: If document doesn't exist
        """
        document = self.repository.get_or_raise(document_id)
        return self.repository.update_processing_status(document, status)

