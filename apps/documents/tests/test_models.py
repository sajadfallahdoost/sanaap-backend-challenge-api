"""
Tests for document models.
"""
import pytest
from apps.documents.models import Document
from apps.authentication.models import User


@pytest.mark.django_db
class TestDocumentModel:
    """Test Document model."""
    
    def test_create_document(self, admin_user):
        """Test creating a document."""
        document = Document.objects.create(
            title='Test Document',
            description='Test description',
            file_path='users/1/test.pdf',
            file_type='application/pdf',
            file_extension='pdf',
            size=1024,
            uploaded_by=admin_user
        )
        
        assert document.id is not None
        assert document.title == 'Test Document'
        assert document.uploaded_by == admin_user
        assert document.processing_status == Document.ProcessingStatus.PENDING
    
    def test_document_is_image_property(self, admin_user):
        """Test is_image property."""
        image_doc = Document.objects.create(
            title='Image',
            file_path='test.jpg',
            file_type='image/jpeg',
            file_extension='jpg',
            size=1024,
            uploaded_by=admin_user
        )
        
        pdf_doc = Document.objects.create(
            title='PDF',
            file_path='test.pdf',
            file_type='application/pdf',
            file_extension='pdf',
            size=1024,
            uploaded_by=admin_user
        )
        
        assert image_doc.is_image is True
        assert pdf_doc.is_image is False
    
    def test_document_string_representation(self, admin_user):
        """Test document __str__ method."""
        document = Document.objects.create(
            title='My Document',
            file_path='test.pdf',
            file_type='application/pdf',
            file_extension='pdf',
            size=1024,
            uploaded_by=admin_user
        )
        
        assert str(document) == 'My Document (pdf)'

