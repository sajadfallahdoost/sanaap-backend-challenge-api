"""
Admin interface configuration for document models.
"""
from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin interface for Document model."""
    
    list_display = [
        'title', 'file_extension', 'uploaded_by', 
        'processing_status', 'created_at'
    ]
    list_filter = [
        'file_extension', 'processing_status', 
        'created_at', 'uploaded_by'
    ]
    search_fields = ['title', 'description', 'file_path']
    readonly_fields = ['created_at', 'updated_at', 'file_path', 'size']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Document Information', {
            'fields': ('title', 'description', 'file_path', 'file_type', 'file_extension', 'size')
        }),
        ('Upload Details', {
            'fields': ('uploaded_by', 'processing_status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

