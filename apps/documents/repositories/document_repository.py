"""
Repository for Document model data access operations.

This module implements the repository pattern for Document model,
providing clean data access abstractions.
"""
from typing import Optional, List
from django.db.models import QuerySet, Q
from datetime import datetime
from apps.common.repositories import BaseRepository
from apps.documents.models import Document
from apps.authentication.models import User


class DocumentRepository(BaseRepository[Document]):
    """
    Repository for Document model operations.
    
    Provides optimized queries and data access methods for documents,
    following the repository pattern for clean separation of concerns.
    """
    
    def __init__(self):
        """Initialize repository with Document model."""
        super().__init__(Document)
    
    def get_by_id_with_user(self, document_id: int) -> Optional[Document]:
        """
        Get document by ID with related user data prefetched.
        
        Args:
            document_id: Document ID
            
        Returns:
            Document instance with user data, or None
        """
        try:
            return self.select_related('uploaded_by').get(pk=document_id)
        except Document.DoesNotExist:
            return None
    
    def get_user_documents(self, user: User) -> QuerySet[Document]:
        """
        Get all documents uploaded by a specific user.
        
        Args:
            user: User instance
            
        Returns:
            QuerySet of documents uploaded by the user
        """
        return self.filter(uploaded_by=user).select_related('uploaded_by')
    
    def filter_documents(
        self,
        file_type: Optional[str] = None,
        file_extension: Optional[str] = None,
        uploaded_by: Optional[User] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        search_query: Optional[str] = None,
        processing_status: Optional[str] = None
    ) -> QuerySet[Document]:
        """
        Filter documents by various criteria.
        
        Args:
            file_type: Filter by MIME type
            file_extension: Filter by file extension
            uploaded_by: Filter by uploader
            start_date: Filter documents created after this date
            end_date: Filter documents created before this date
            search_query: Search in title and description
            processing_status: Filter by processing status
            
        Returns:
            QuerySet of filtered documents
        """
        queryset = self.select_related('uploaded_by').all()
        
        if file_type:
            queryset = queryset.filter(file_type__icontains=file_type)
        
        if file_extension:
            queryset = queryset.filter(file_extension__iexact=file_extension)
        
        if uploaded_by:
            queryset = queryset.filter(uploaded_by=uploaded_by)
        
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        if processing_status:
            queryset = queryset.filter(processing_status=processing_status)
        
        return queryset
    
    def get_by_file_path(self, file_path: str) -> Optional[Document]:
        """
        Get document by file path.
        
        Args:
            file_path: File path in storage
            
        Returns:
            Document instance if found, None otherwise
        """
        try:
            return self.model.objects.get(file_path=file_path)
        except Document.DoesNotExist:
            return None
    
    def get_pending_documents(self) -> QuerySet[Document]:
        """
        Get all documents pending processing.
        
        Returns:
            QuerySet of documents with pending status
        """
        return self.filter(
            processing_status=Document.ProcessingStatus.PENDING
        ).select_related('uploaded_by')
    
    def get_failed_documents(self) -> QuerySet[Document]:
        """
        Get all documents with failed processing.
        
        Returns:
            QuerySet of documents with failed status
        """
        return self.filter(
            processing_status=Document.ProcessingStatus.FAILED
        ).select_related('uploaded_by')
    
    def update_processing_status(
        self,
        document: Document,
        status: str
    ) -> Document:
        """
        Update document processing status.
        
        Args:
            document: Document instance
            status: New processing status
            
        Returns:
            Updated document instance
        """
        return self.update(document, processing_status=status)
    
    def get_recent_documents(self, limit: int = 10) -> QuerySet[Document]:
        """
        Get most recently uploaded documents.
        
        Args:
            limit: Maximum number of documents to return
            
        Returns:
            QuerySet of recent documents
        """
        return self.select_related('uploaded_by').all()[:limit]
    
    def get_documents_by_extensions(
        self,
        extensions: List[str]
    ) -> QuerySet[Document]:
        """
        Get documents with specific file extensions.
        
        Args:
            extensions: List of file extensions
            
        Returns:
            QuerySet of matching documents
        """
        return self.filter(
            file_extension__in=[ext.lower() for ext in extensions]
        ).select_related('uploaded_by')

