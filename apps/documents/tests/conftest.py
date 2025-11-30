"""
Pytest fixtures for document tests.
"""
import pytest
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.authentication.models import User
from apps.documents.models import Document


@pytest.fixture
def test_image_file():
    """Create a test image file."""
    file_data = BytesIO(b"fake image data")
    return SimpleUploadedFile(
        "test_image.jpg",
        file_data.getvalue(),
        content_type="image/jpeg"
    )


@pytest.fixture
def test_pdf_file():
    """Create a test PDF file."""
    file_data = BytesIO(b"fake pdf data")
    return SimpleUploadedFile(
        "test_document.pdf",
        file_data.getvalue(),
        content_type="application/pdf"
    )


@pytest.fixture
def sample_document(db, admin_user):
    """Create a sample document for testing."""
    return Document.objects.create(
        title='Sample Document',
        description='Test description',
        file_path='users/1/2024/test.jpg',
        file_type='image/jpeg',
        file_extension='jpg',
        size=1024,
        uploaded_by=admin_user,
        processing_status=Document.ProcessingStatus.COMPLETED
    )


@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    return User.objects.create_user(
        username='admin',
        email='admin@test.com',
        password='admin123',
        role=User.Role.ADMIN
    )


@pytest.fixture
def editor_user(db):
    """Create an editor user."""
    return User.objects.create_user(
        username='editor',
        email='editor@test.com',
        password='editor123',
        role=User.Role.EDITOR
    )

