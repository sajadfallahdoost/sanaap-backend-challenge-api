"""
Serializers for audit logging.

This module defines serializers for audit log data
for API requests and responses.
"""
from rest_framework import serializers
from apps.audit.models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    """
    Serializer for AuditLog model.
    
    Provides complete audit log information.
    """
    
    username = serializers.CharField(source='user.username', read_only=True, allow_null=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    resource_type_display = serializers.CharField(source='get_resource_type_display', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'username', 'action', 'action_display',
            'resource_type', 'resource_type_display', 'resource_id',
            'ip_address', 'user_agent', 'details', 'timestamp'
        ]
        read_only_fields = fields

