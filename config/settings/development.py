"""
Development settings for Document Management System.

These settings are used during local development.
DO NOT use these settings in production.
"""
from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

# CORS - Allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True

# Security settings - DISABLED for development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False

# Static files - serve directly in development
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Email backend for development (console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Django Debug Toolbar (optional - commented out by default)
# To enable: pip install django-debug-toolbar and uncomment below
# INSTALLED_APPS += ['django_debug_toolbar']
# MIDDLEWARE += ['django_debug_toolbar.middleware.DebugToolbarMiddleware']
# INTERNAL_IPS = ['127.0.0.1', 'localhost', '0.0.0.0']

# Disable template caching in development
TEMPLATES[0]['OPTIONS']['debug'] = True

# Additional logging for development
LOGGING['root']['level'] = 'INFO'  # Changed to INFO to reduce noise
LOGGING['loggers']['apps']['level'] = 'DEBUG'

