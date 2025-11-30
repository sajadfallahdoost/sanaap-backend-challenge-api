"""
Notification service for real-time document events.

This module handles broadcasting document events via WebSocket
using Django Channels.
"""
from typing import Optional
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import datetime
from apps.authentication.models import User
from apps.documents.models import Document
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service for broadcasting real-time notifications.
    
    Handles sending document events to WebSocket clients via Django Channels.
    """
    
    def __init__(self):
        """Initialize notification service with channel layer."""
        self.channel_layer = get_channel_layer()
    
    def _broadcast_event(
        self,
        event_type: str,
        document: Document,
        user: User,
        additional_data: Optional[dict] = None
    ) -> None:
        """
        Broadcast an event to all connected WebSocket clients.
        
        Args:
            event_type: Type of event (created, updated, deleted)
            document: Document instance
            user: User who performed the action
            additional_data: Additional event data
        """
        if not self.channel_layer:
            logger.warning("Channel layer not configured, skipping notification")
            return
        
        # Prepare notification payload
        notification = {
            'type': 'document_notification',  # Method name in consumer
            'event_type': event_type,
            'document': {
                'id': document.id,
                'title': document.title,
                'file_extension': document.file_extension,
                'file_type': document.file_type,
            },
            'user': {
                'id': user.id,
                'username': user.username,
            },
            'timestamp': datetime.now().isoformat(),
        }
        
        if additional_data:
            notification.update(additional_data)
        
        # Broadcast to group
        try:
            async_to_sync(self.channel_layer.group_send)(
                'document_notifications',
                notification
            )
            logger.debug(
                f"Broadcast {event_type} notification for document {document.id}"
            )
        except Exception as e:
            logger.error(f"Failed to broadcast notification: {str(e)}")
    
    def notify_document_created(self, document: Document, user: User) -> None:
        """
        Notify that a new document was created.
        
        Args:
            document: Created document
            user: User who created the document
        """
        self._broadcast_event(
            event_type='document.created',
            document=document,
            user=user
        )
    
    def notify_document_updated(self, document: Document, user: User) -> None:
        """
        Notify that a document was updated.
        
        Args:
            document: Updated document
            user: User who updated the document
        """
        self._broadcast_event(
            event_type='document.updated',
            document=document,
            user=user
        )
    
    def notify_document_deleted(
        self,
        document_id: int,
        document_title: str,
        user: User
    ) -> None:
        """
        Notify that a document was deleted.
        
        Args:
            document_id: ID of deleted document
            document_title: Title of deleted document
            user: User who deleted the document
        """
        # Create a minimal document-like object for the notification
        class DeletedDocument:
            id = document_id
            title = document_title
            file_extension = ''
            file_type = ''
        
        self._broadcast_event(
            event_type='document.deleted',
            document=DeletedDocument(),
            user=user
        )


# Singleton instance
_notification_service: Optional[NotificationService] = None


def get_notification_service() -> NotificationService:
    """
    Get or create the notification service singleton.
    
    Returns:
        NotificationService instance
    """
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service

