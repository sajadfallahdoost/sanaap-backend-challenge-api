# Document Management System (DMS) API

A professional, production-ready Document Management System built with Django REST Framework, featuring role-based access control, real-time notifications, audit logging, and scalable architecture.

## Features

### Core Functionality
- **Secure Document Management**: Upload, retrieve, update, and delete documents with MinIO object storage
- **Role-Based Access Control (RBAC)**: Three-tier permission system (Admin, Editor, Viewer)
- **Real-Time Notifications**: WebSocket support via Django Channels for instant updates
- **Background Processing**: Celery integration for asynchronous document processing
- **Comprehensive Audit Logging**: Track all user actions and document operations
- **Advanced Filtering & Pagination**: Efficient document search and navigation
- **RESTful API**: Well-documented API with Swagger/OpenAPI support

### Security Features
- JWT authentication with token refresh
- Secure file upload validation
- Rate limiting via Django middleware
- RBAC enforcement at multiple layers
- Presigned URL generation for secure file access
- Comprehensive input validation

### Technical Excellence
- **Clean Architecture**: Repository and Service patterns
- **SOLID Principles**: Maintainable and extensible codebase
- **Comprehensive Testing**: Unit and integration tests with 80%+ coverage
- **Docker Support**: Full containerization with Docker Compose
- **Production-Ready**: Gunicorn and professional deployment setup
- **Scalable Design**: Horizontal and vertical scaling support

## Quick Start

### Using Docker Compose (Recommended) - Development Mode

1. **Clone the repository**
```bash
git clone <repository-url>
cd sanaap-backend-challenge-api
```

2. **Start all services**
```bash
docker-compose up -d
```

That's it! The system automatically handles:
- ✅ Database migrations
- ✅ Creating superuser (username: `admin`, password: `admin123`)
- ✅ Collecting static files
- ✅ Initializing MinIO bucket
- ✅ Starting all services in **Development Mode**

**Development Mode Features:**
- 🔥 Auto-reload on code changes (no restart needed!)
- 🐛 DEBUG mode enabled with detailed error pages
- 📦 Static files served automatically by Django
- ⚡ Fast development workflow

3. **Access the application**
- **Admin Panel**: http://localhost:8000/admin
  - Username: `admin`
  - Password: `admin123`
  - ✅ CSS/JS loads perfectly!
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs/
- **MinIO Console**: http://localhost:9001
  - Username: `minioadmin`
  - Password: `minioadmin`

4. **View logs**
```bash
# All containers
docker-compose logs -f

# Specific service
docker-compose logs -f web
```

5. **Stop services**
```bash
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

### Manual Setup

**Prerequisites:**
- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- MinIO

**Installation:**

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/dev.txt

# Set up database
createdb dms_db

# Configure environment
# Optional: Set environment variables if you want to override defaults
# All variables have sensible defaults in code, so this step is optional

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# In separate terminals:
# Run Celery worker
celery -A config worker -l info

# Run Celery beat
celery -A config beat -l info

# Run Daphne (WebSocket)
daphne -b 0.0.0.0 -p 9000 config.asgi:application
```

## API Documentation

### Authentication

**Login**
```bash
POST /api/auth/login/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**Response**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin"
  }
}
```

### Document Upload

```bash
POST /api/documents/upload/
Authorization: Bearer <your_token>
Content-Type: multipart/form-data

file: <binary_file>
title: "My Document"
description: "Optional description"
```

### Complete API Endpoints

| Endpoint | Method | Description | Permission |
|----------|--------|-------------|------------|
| `/api/auth/login/` | POST | User login | Public |
| `/api/auth/me/` | GET | Current user info | Authenticated |
| `/api/documents/` | GET | List documents | Authenticated |
| `/api/documents/upload/` | POST | Upload document | Editor/Admin |
| `/api/documents/{id}/` | GET | Document details | Authenticated |
| `/api/documents/{id}/download/` | GET | Download URL | Authenticated |
| `/api/documents/{id}/update/` | PUT/PATCH | Update document | Editor/Admin |
| `/api/documents/{id}/delete/` | DELETE | Delete document | Admin only |
| `/api/audit/logs/` | GET | Audit logs | Admin only |

**Full Documentation:** http://localhost:8000/api/docs/

## User Roles

### Admin
- Full system access
- Create, read, update, and delete all documents
- Manage users and assign roles
- Access audit logs
- Upload any file type

### Editor
- Upload and update **images only** (jpg, jpeg, png, gif, webp)
- Can only modify their own documents
- Cannot delete documents
- Cannot access admin features

### Viewer
- Read-only access
- View and download documents
- Cannot upload or modify content

## Project Structure

```
sanaap-backend-challenge-api/
├── apps/                      # Django applications
│   ├── authentication/        # User auth & RBAC
│   ├── documents/            # Document management
│   ├── audit/                # Audit logging
│   └── common/               # Shared utilities
├── config/                   # Django settings
│   ├── settings/            # Split settings (base, dev, prod)
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── infrastructure/           # External services
│   ├── storage/             # MinIO client
│   ├── cache/               # Redis cache
│   └── messaging/           # WebSocket utilities
├── docs/                    # Documentation
│   ├── api/                 # API documentation
│   ├── architecture/        # System design
│   ├── database/            # Database schema
│   ├── deployment/          # Deployment guide
│   └── development/         # Development guide
├── docker/                  # Docker configuration
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── scripts/            # Docker scripts
├── requirements/            # Python dependencies
└── README.md               # This file
```

## Technology Stack

- **Backend**: Django 4.2.7, Django REST Framework 3.14
- **Database**: PostgreSQL 15
- **Cache/Queue**: Redis 7
- **Storage**: MinIO
- **Task Queue**: Celery 5.3
- **WebSocket**: Django Channels 4.0
- **Web Server**: Gunicorn
- **Containerization**: Docker + Docker Compose

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps --cov-report=html

# Run specific app tests
pytest apps/documents/tests/

# View coverage report
open htmlcov/index.html
```

## Development

### Code Quality Tools

```bash
# Format code
black apps/

# Sort imports
isort apps/

# Lint code
flake8 apps/

# Type checking
mypy apps/
```

### Creating Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# View SQL
python manage.py sqlmigrate app_name migration_number
```

## Deployment

### Production Deployment

See detailed deployment guide: [docs/deployment/README.md](docs/deployment/README.md)

**Quick production deployment:**

```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

### Environment Variables

All environment variables are optional and have sensible defaults in code. You can override them by setting environment variables:

```bash
# Django (optional - defaults provided in code)
SECRET_KEY=your-secret-key-here  # Default: insecure key for development
DEBUG=False  # Default: False
ALLOWED_HOSTS=your-domain.com  # Default: localhost,127.0.0.1

# Database (optional - defaults provided in code)
DB_NAME=dms_db  # Default: dms_db
DB_USER=postgres  # Default: postgres
DB_PASSWORD=strong-password  # Default: postgres
DB_HOST=db  # Default: localhost
DB_PORT=5432  # Default: 5432

# MinIO (optional - defaults provided in code)
MINIO_ENDPOINT=minio:9000  # Default: localhost:9000
MINIO_ACCESS_KEY=your-access-key  # Default: minioadmin
MINIO_SECRET_KEY=your-secret-key  # Default: minioadmin
MINIO_BUCKET_NAME=documents  # Default: documents

# Redis (optional - defaults provided in code)
REDIS_URL=redis://redis:6379/1  # Default: redis://localhost:6379/1
CELERY_BROKER_URL=redis://redis:6379/0  # Default: redis://localhost:6379/0
```

**Note:** For production, you **must** set `SECRET_KEY` as a secure environment variable. The default insecure key will cause the application to raise an error in production mode.

## Architecture Highlights

### Clean Architecture
- **Repository Pattern**: Data access abstraction
- **Service Layer**: Business logic separation
- **SOLID Principles**: Maintainable design
- **Dependency Injection**: Loosely coupled components

### Security
- JWT authentication with refresh tokens
- Role-based permissions at multiple layers
- File validation and sanitization
- Secure presigned URLs with expiration
- Rate limiting and DDoS protection

### Scalability
- Stateless application design
- Horizontal scaling support
- Background task processing
- Connection pooling
- Caching strategies

## WebSocket Notifications

Connect to real-time document notifications:

```javascript
const socket = new WebSocket('ws://localhost:9000/ws/documents/notifications/');

socket.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Document notification:', data);
  // Handle: document.created, document.updated
};
```

## Monitoring & Logging

- **Application Logs**: `/app/logs/django.log`
- **Celery Logs**: Worker and beat scheduler logs
- **Gunicorn Logs**: Application server logs
- **Audit Logs**: Database-stored audit trail

## Performance

- Database query optimization with select_related/prefetch_related
- Redis caching for frequently accessed data
- Celery for asynchronous processing
- Django static file serving
- Connection pooling

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is proprietary software developed for Sanaap interview challenge.

## Support

For issues, questions, or contributions, please contact the development team.

---

**Built with ❤️ following enterprise best practices**

