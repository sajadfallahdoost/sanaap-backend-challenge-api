"""
Configuration package for the Document Management System.
"""
from .celery import app as celery_app

__all__ = ('celery_app',)

