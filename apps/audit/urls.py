"""
URL patterns for audit log endpoints.
"""
from django.urls import path
from . import views

app_name = 'audit'

urlpatterns = [
    path('logs/', views.list_audit_logs_view, name='list_logs'),
    path('logs/export/', views.export_audit_logs_view, name='export_logs'),
]

