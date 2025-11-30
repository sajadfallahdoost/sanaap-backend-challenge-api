# Development Guide

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- MinIO (for local development)
- Git

### Local Development Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd sanaap-backend-challenge-api
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements/dev.txt
```

4. **Set up PostgreSQL**
```bash
# Create database
createdb dms_db

# Or using psql
psql -U postgres
CREATE DATABASE dms_db;
CREATE USER dms_user WITH PASSWORD 'dms_password';
GRANT ALL PRIVILEGES ON DATABASE dms_db TO dms_user;
\q
```

5. **Set up Redis**
```bash
# Install Redis (Ubuntu/Debian)
sudo apt install redis-server
sudo systemctl start redis

# Or using Docker
docker run -d -p 6379:6379 redis:latest
```

6. **Set up MinIO**
```bash
# Using Docker
docker run -d \
  -p 9000:9000 \
  -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  minio/minio server /data --console-address ":9001"
```

7. **Configure environment (optional)**
```bash
# Environment variables are optional - all have defaults in code
# You can set them as system environment variables if you want to override defaults
```

8. **Run migrations**
```bash
python manage.py migrate
```

9. **Create superuser**
```bash
python manage.py createsuperuser
```

10. **Run development server**
```bash
python manage.py runserver
```

11. **Run Celery worker (separate terminal)**
```bash
celery -A config worker -l info
```

12. **Run Celery beat (separate terminal)**
```bash
celery -A config beat -l info
```

13. **Run Channels/Daphne (separate terminal)**
```bash
daphne -b 0.0.0.0 -p 9000 config.asgi:application
```

## Project Structure

```
sanaap-backend-challenge-api/
├── apps/                          # Django applications
│   ├── authentication/            # User auth and RBAC
│   │   ├── models.py             # User model
│   │   ├── repositories/         # Data access layer
│   │   ├── services/             # Business logic
│   │   ├── views.py              # API endpoints
│   │   ├── serializers.py        # DRF serializers
│   │   ├── permissions.py        # Custom permissions
│   │   ├── urls.py               # URL routing
│   │   └── tests/                # Tests
│   ├── documents/                # Document management
│   │   ├── models.py             # Document model
│   │   ├── repositories/         # Data access layer
│   │   ├── services/             # Business logic
│   │   ├── tasks.py              # Celery tasks
│   │   ├── consumers.py          # WebSocket consumers
│   │   ├── views.py              # API endpoints
│   │   ├── serializers.py        # DRF serializers
│   │   ├── filters.py            # Query filters
│   │   ├── utils/                # Utilities
│   │   ├── routing.py            # WebSocket routing
│   │   ├── urls.py               # URL routing
│   │   └── tests/                # Tests
│   ├── audit/                    # Audit logging
│   │   ├── models.py             # AuditLog model
│   │   ├── repositories/         # Data access layer
│   │   ├── services/             # Business logic
│   │   ├── views.py              # API endpoints
│   │   ├── serializers.py        # DRF serializers
│   │   ├── urls.py               # URL routing
│   │   └── tests/                # Tests
│   └── common/                   # Shared utilities
│       ├── exceptions.py         # Custom exceptions
│       ├── decorators.py         # Custom decorators
│       └── repositories/         # Base repository
├── config/                       # Django project configuration
│   ├── settings/                 # Split settings
│   │   ├── base.py              # Base settings
│   │   ├── development.py       # Dev settings
│   │   └── production.py        # Prod settings
│   ├── urls.py                  # Root URL configuration
│   ├── wsgi.py                  # WSGI application
│   ├── asgi.py                  # ASGI application
│   └── celery.py                # Celery configuration
├── infrastructure/              # Infrastructure layer
│   ├── storage/                 # MinIO client
│   ├── cache/                   # Cache utilities
│   └── messaging/               # Messaging utilities
├── docs/                        # Documentation
│   ├── api/                     # API documentation
│   ├── architecture/            # Architecture docs
│   ├── database/                # Database schema
│   ├── deployment/              # Deployment guide
│   └── development/             # Development guide
├── docker/                      # Docker configuration
│   ├── Dockerfile              # Docker image
│   ├── docker-compose.yml      # Compose file
│   ├── nginx/                  # Nginx config
│   └── scripts/                # Deployment scripts
├── requirements/                # Python dependencies
│   ├── base.txt                # Base requirements
│   ├── dev.txt                 # Dev requirements
│   └── prod.txt                # Prod requirements
├── manage.py                    # Django management
# Environment variables are handled in code with defaults
├── .gitignore                   # Git ignore rules
└── README.md                    # Main README
```

## Code Standards

### Python Style Guide

Follow PEP 8 with these specific rules:

```python
# Imports order
import os                    # Standard library
from typing import Optional  # Standard library

from django.db import models # Third-party
from rest_framework import serializers

from apps.common.exceptions import ValidationError  # Local

# Line length: 100 characters max
# Use type hints
def function_name(param: str) -> Optional[int]:
    """
    Docstring explaining the function.
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
    """
    pass

# Class names: PascalCase
class DocumentService:
    pass

# Functions/methods: snake_case
def upload_document():
    pass

# Constants: UPPER_SNAKE_CASE
MAX_UPLOAD_SIZE = 50 * 1024 * 1024
```

### Docstring Format

Use Google-style docstrings:

```python
def complex_function(arg1: str, arg2: int = 0) -> dict:
    """
    Brief description of function.
    
    More detailed description if needed. Can span
    multiple lines.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2 (default: 0)
        
    Returns:
        Dictionary containing result data
        
    Raises:
        ValidationError: If arg1 is empty
        PermissionDeniedError: If user lacks permission
        
    Example:
        >>> result = complex_function("test", 5)
        >>> print(result['status'])
        'success'
    """
    pass
```

### Code Quality Tools

**Black** - Code formatting:
```bash
black apps/
```

**isort** - Import sorting:
```bash
isort apps/
```

**flake8** - Linting:
```bash
flake8 apps/
```

**mypy** - Type checking:
```bash
mypy apps/
```

**Pre-commit hook** (`.git/hooks/pre-commit`):
```bash
#!/bin/bash
black --check apps/
isort --check apps/
flake8 apps/
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific app tests
pytest apps/authentication/tests/

# Run with coverage
pytest --cov=apps --cov-report=html

# Run specific test file
pytest apps/documents/tests/test_services.py

# Run specific test
pytest apps/documents/tests/test_services.py::TestDocumentService::test_upload_document
```

### Writing Tests

**Test file structure:**
```
apps/documents/tests/
├── __init__.py
├── test_models.py
├── test_repositories.py
├── test_services.py
├── test_views.py
├── test_tasks.py
├── conftest.py          # Pytest fixtures
└── factories.py         # Factory Boy factories
```

**Example test:**
```python
import pytest
from apps.documents.services import DocumentService
from apps.documents.tests.factories import DocumentFactory, UserFactory

@pytest.mark.django_db
class TestDocumentService:
    def setup_method(self):
        self.service = DocumentService()
        self.user = UserFactory(role='editor')
    
    def test_upload_document_success(self):
        """Test successful document upload."""
        # Arrange
        file = create_test_file('test.jpg')
        
        # Act
        document = self.service.upload_document(
            file=file,
            title='Test Document',
            user=self.user
        )
        
        # Assert
        assert document.id is not None
        assert document.title == 'Test Document'
        assert document.uploaded_by == self.user
    
    def test_upload_document_invalid_extension(self):
        """Test upload fails with invalid extension."""
        file = create_test_file('test.exe')
        
        with pytest.raises(ValidationError):
            self.service.upload_document(
                file=file,
                title='Test',
                user=self.user
            )
```

### Test Factories

Use Factory Boy for test data:

```python
# factories.py
import factory
from apps.authentication.models import User
from apps.documents.models import Document

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    role = 'viewer'

class DocumentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Document
    
    title = factory.Sequence(lambda n: f'Document {n}')
    file_path = factory.Sequence(lambda n: f'docs/file{n}.pdf')
    file_type = 'application/pdf'
    file_extension = 'pdf'
    size = 1024
    uploaded_by = factory.SubFactory(UserFactory)
```

## Database Migrations

### Creating Migrations

```bash
# Create migrations after model changes
python manage.py makemigrations

# Create empty migration for data migration
python manage.py makemigrations --empty app_name

# Check migration status
python manage.py showmigrations

# SQL preview
python manage.py sqlmigrate app_name migration_number
```

### Data Migration Example

```python
# Migration file
from django.db import migrations

def populate_default_users(apps, schema_editor):
    User = apps.get_model('authentication', 'User')
    User.objects.create(
        username='admin',
        email='admin@example.com',
        role='admin',
        is_staff=True
    )

class Migration(migrations.Migration):
    dependencies = [
        ('authentication', '0001_initial'),
    ]
    
    operations = [
        migrations.RunPython(populate_default_users),
    ]
```

## API Development

### Adding New Endpoint

1. **Create serializer** (`serializers.py`):
```python
class NewFeatureSerializer(serializers.Serializer):
    field1 = serializers.CharField()
    field2 = serializers.IntegerField()
```

2. **Add business logic** (`services/feature_service.py`):
```python
class FeatureService:
    def process_feature(self, data):
        # Business logic here
        pass
```

3. **Create view** (`views.py`):
```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def feature_view(request):
    serializer = NewFeatureSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    # Use service
    result = service.process_feature(serializer.validated_data)
    return Response(result)
```

4. **Add URL** (`urls.py`):
```python
urlpatterns = [
    path('feature/', views.feature_view, name='feature'),
]
```

5. **Write tests** (`tests/test_views.py`):
```python
def test_feature_endpoint():
    # Test implementation
    pass
```

## Debugging

### Django Debug Toolbar

```python
# Already configured in development.py
# Access at: http://localhost:8000/__debug__/
```

### IPython Shell

```bash
python manage.py shell_plus

# In shell
>>> from apps.documents.models import Document
>>> Document.objects.all()
```

### Debug Logging

```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

## Git Workflow

### Branch Naming

- `feature/feature-name` - New features
- `bugfix/bug-name` - Bug fixes
- `hotfix/issue-name` - Critical fixes
- `refactor/component-name` - Code refactoring

### Commit Messages

Follow conventional commits:

```
type(scope): subject

body

footer
```

Examples:
```
feat(documents): add PDF support
fix(auth): resolve token expiration issue
docs(api): update authentication documentation
refactor(services): simplify document upload logic
test(documents): add upload validation tests
```

### Pull Request Process

1. Create feature branch
2. Implement changes
3. Write tests
4. Update documentation
5. Run tests and linters
6. Create pull request
7. Address review comments
8. Merge after approval

## Performance Optimization

### Database Query Optimization

```python
# Bad - N+1 query problem
documents = Document.objects.all()
for doc in documents:
    print(doc.uploaded_by.username)  # Extra query per document

# Good - Use select_related
documents = Document.objects.select_related('uploaded_by').all()
for doc in documents:
    print(doc.uploaded_by.username)  # No extra queries
```

### Caching

```python
from django.core.cache import cache

# Cache expensive operation
def get_statistics():
    stats = cache.get('document_stats')
    if stats is None:
        stats = calculate_statistics()
        cache.set('document_stats', stats, 3600)  # Cache for 1 hour
    return stats
```

## Troubleshooting

### Common Development Issues

**Issue: Migration conflicts**
```bash
python manage.py makemigrations --merge
```

**Issue: Cached imports after code changes**
```bash
# Restart development server
# Or use auto-reload tools
```

**Issue: Test database not cleaned between runs**
```bash
pytest --create-db
```

## Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [DRF Documentation](https://www.django-rest-framework.org/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Django Channels](https://channels.readthedocs.io/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

