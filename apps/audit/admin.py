"""
Admin interface configuration for audit models.
"""
from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin interface for AuditLog model."""
    
    list_display = [
        'timestamp', 'user', 'action', 'resource_type',
        'resource_id', 'ip_address'
    ]
    list_filter = [
        'action', 'resource_type', 'timestamp'
    ]
    search_fields = [
        'user__username', 'ip_address', 'action'
    ]
    readonly_fields = [
        'user', 'action', 'resource_type', 'resource_id',
        'ip_address', 'user_agent', 'details', 'timestamp'
    ]
    ordering = ['-timestamp']
    
    def has_add_permission(self, request):
        """Prevent manual creation of audit logs."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of audit logs."""
        return False

