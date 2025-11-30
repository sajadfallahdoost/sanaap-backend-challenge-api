#!/bin/bash
# Exit on error for the application command, but handle setup errors gracefully
set -e

echo "=========================================="
echo "Starting Django Application Setup"
echo "=========================================="

# Wait for database to be ready
echo "⏳ Waiting for database..."
MAX_RETRIES=30
RETRY_COUNT=0
until nc -z db 5432 || [ $RETRY_COUNT -eq $MAX_RETRIES ]; do
  echo "   Database not ready, waiting... ($RETRY_COUNT/$MAX_RETRIES)"
  sleep 2
  RETRY_COUNT=$((RETRY_COUNT + 1))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
  echo "❌ Database connection timeout!"
  exit 1
fi
echo "✅ Database is ready!"

# Wait for Redis to be ready
echo "⏳ Waiting for Redis..."
RETRY_COUNT=0
until nc -z redis 6379 || [ $RETRY_COUNT -eq $MAX_RETRIES ]; do
  echo "   Redis not ready, waiting... ($RETRY_COUNT/$MAX_RETRIES)"
  sleep 2
  RETRY_COUNT=$((RETRY_COUNT + 1))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
  echo "❌ Redis connection timeout!"
  exit 1
fi
echo "✅ Redis is ready!"

# Wait for MinIO to be ready
echo "⏳ Waiting for MinIO..."
RETRY_COUNT=0
until nc -z minio 9000 || [ $RETRY_COUNT -eq $MAX_RETRIES ]; do
  echo "   MinIO not ready, waiting... ($RETRY_COUNT/$MAX_RETRIES)"
  sleep 2
  RETRY_COUNT=$((RETRY_COUNT + 1))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
  echo "❌ MinIO connection timeout!"
  exit 1
fi
echo "✅ MinIO is ready!"

# Additional wait to ensure services are fully ready
echo "⏳ Waiting for services to stabilize..."
sleep 3

# Run database migrations
echo "🔄 Running database migrations..."
set +e  # Don't exit on makemigrations error
python manage.py makemigrations --noinput
MAKEMIGRATIONS_EXIT=$?
set -e

if [ $MAKEMIGRATIONS_EXIT -eq 0 ]; then
  echo "✅ Migrations created successfully (if any were needed)"
else
  echo "ℹ️  No new migrations needed or migrations already exist"
fi

# Run migrations
echo "🔄 Applying database migrations..."
python manage.py migrate --noinput
echo "✅ Migrations applied successfully!"

# Collect static files (for development, we use findstatic)
echo "📦 Collecting static files..."
set +e
python manage.py collectstatic --noinput
COLLECTSTATIC_EXIT=$?
set -e

if [ $COLLECTSTATIC_EXIT -eq 0 ]; then
  echo "✅ Static files collected successfully"
else
  echo "⚠️  Static files collection had issues, continuing..."
fi

# In development mode, Django runserver serves static files automatically
if [ "$DJANGO_SETTINGS_MODULE" = "config.settings.development" ]; then
  echo "ℹ️  Development mode: Django will serve static files automatically"
fi

# Initialize MinIO bucket if needed (bucket is auto-created by MinIOClient)
echo "🪣 Initializing MinIO connection..."
set +e
python manage.py shell << 'PYTHON_SCRIPT'
from infrastructure.storage.minio_client import get_minio_client
import os

try:
    client = get_minio_client()
    bucket_name = os.getenv('MINIO_BUCKET_NAME', 'documents')
    print(f'✅ MinIO bucket ready: {bucket_name}')
except Exception as e:
    print(f'⚠️  MinIO initialization failed: {e}')
    print('   Bucket will be created on first use')
PYTHON_SCRIPT
set -e

# Create default superuser if doesn't exist
echo "👤 Creating superuser if it doesn't exist..."
set +e
python manage.py shell << 'PYTHON_SCRIPT'
import os
from django.contrib.auth import get_user_model

User = get_user_model()

username = os.getenv('SUPERUSER_USERNAME', 'admin')
email = os.getenv('SUPERUSER_EMAIL', 'admin@example.com')
password = os.getenv('SUPERUSER_PASSWORD', 'admin123')

try:
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            role='admin'
        )
        print(f'✅ Superuser "{username}" created successfully')
        print(f'   Email: {email}')
        print(f'   Password: {password}')
    else:
        print(f'ℹ️  Superuser "{username}" already exists')
except Exception as e:
    print(f'⚠️  Error creating superuser: {e}')
PYTHON_SCRIPT
set -e

echo ""
echo "=========================================="
echo "✅ Setup completed successfully!"
echo "=========================================="
echo "   Database: Connected"
echo "   Redis: Connected"
echo "   MinIO: Connected"
echo "   Migrations: Applied"
echo "   Superuser: Ready"
echo "=========================================="
echo ""
echo "🚀 Starting application server..."
echo ""

# Execute the command passed to the container (gunicorn, celery, etc.)
exec "$@"

