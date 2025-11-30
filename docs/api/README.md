# API Documentation

## Overview

The Document Management System (DMS) provides a RESTful API built with Django REST Framework. All endpoints require authentication via JWT tokens except for the login endpoint.

## Base URL

```
http://localhost:8000/api/
```

## Authentication

The API uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_access_token>
```

### Obtain Tokens

**Endpoint:** `POST /api/auth/login/`

**Request:**
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**Response:**
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

### Refresh Token

**Endpoint:** `POST /api/auth/token/refresh/`

**Request:**
```json
{
  "refresh": "your_refresh_token"
}
```

## API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| POST | `/api/auth/login/` | User login | Public |
| POST | `/api/auth/token/refresh/` | Refresh access token | Public |
| GET | `/api/auth/me/` | Get current user info | Authenticated |
| POST | `/api/auth/change-password/` | Change password | Authenticated |
| GET | `/api/auth/users/` | List all users | Admin only |
| POST | `/api/auth/users/create/` | Create new user | Admin only |
| GET | `/api/auth/users/{id}/` | Get user details | Admin only |
| PATCH | `/api/auth/users/{id}/role/` | Update user role | Admin only |

### Document Endpoints

| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/api/documents/` | List documents | Authenticated |
| POST | `/api/documents/upload/` | Upload document | Editor/Admin |
| GET | `/api/documents/{id}/` | Get document details | Authenticated |
| GET | `/api/documents/{id}/download/` | Get download URL | Authenticated |
| PUT/PATCH | `/api/documents/{id}/update/` | Update document | Editor/Admin |
| DELETE | `/api/documents/{id}/delete/` | Delete document | Admin only |

### Audit Log Endpoints

| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/api/audit/logs/` | List audit logs | Admin only |
| GET | `/api/audit/logs/export/` | Export logs to CSV | Admin only |

## Role-Based Access Control

### Admin
- Full system access
- Can create, read, update, and delete all resources
- Can manage users and assign roles
- Can access audit logs

### Editor
- Can upload and update images only (jpg, jpeg, png, gif, webp)
- Can only modify their own documents
- Cannot delete documents
- Cannot access admin features

### Viewer
- Read-only access to documents
- Can view and download documents
- Cannot upload or modify documents

## Document Upload

**Endpoint:** `POST /api/documents/upload/`

**Content-Type:** `multipart/form-data`

**Request:**
```
file: [binary file data]
title: "My Document"
description: "Optional description"
```

**Response:**
```json
{
  "id": 1,
  "title": "My Document",
  "description": "Optional description",
  "file_type": "image/jpeg",
  "file_extension": "jpg",
  "size": 1024567,
  "file_size_display": "1.00 MB",
  "is_image": true,
  "uploaded_by": {
    "id": 2,
    "username": "editor1",
    "role": "editor"
  },
  "processing_status": "pending",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

## Filtering and Pagination

### List Documents with Filters

**Endpoint:** `GET /api/documents/?file_extension=pdf&search=contract&page=1&page_size=20`

**Query Parameters:**
- `file_type`: Filter by MIME type
- `file_extension`: Filter by file extension
- `search`: Search in title and description
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20)

## WebSocket Notifications

Connect to WebSocket for real-time document notifications:

**Endpoint:** `ws://localhost:8000/ws/documents/notifications/`

**Connection:**
```javascript
const socket = new WebSocket('ws://localhost:8000/ws/documents/notifications/');

socket.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Notification:', data);
};
```

**Notification Events:**
- `document.created`: New document uploaded
- `document.updated`: Document modified

**Notification Payload:**
```json
{
  "type": "document.notification",
  "event": "document.created",
  "document": {
    "id": 1,
    "title": "My Document",
    "file_extension": "jpg",
    "file_type": "image/jpeg"
  },
  "user": {
    "id": 2,
    "username": "editor1"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Error Responses

All errors follow a consistent format:

```json
{
  "error": {
    "code": "validation_error",
    "message": "File size exceeds maximum allowed size of 50MB"
  }
}
```

**Common Error Codes:**
- `validation_error`: Input validation failed
- `authentication_error`: Authentication failed
- `permission_denied`: Insufficient permissions
- `not_found`: Resource not found
- `storage_error`: Storage operation failed

## Rate Limiting

API endpoints are rate-limited at the Nginx level:
- 100 requests per minute per IP address
- Burst allowance of 20 requests

## Interactive Documentation

Access interactive API documentation:
- **Swagger UI:** `http://localhost:8000/api/docs/`
- **ReDoc:** `http://localhost:8000/api/redoc/`
- **OpenAPI Schema:** `http://localhost:8000/api/schema/`

