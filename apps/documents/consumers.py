"""
WebSocket consumers for real-time document notifications.

This module implements WebSocket consumers using Django Channels
for broadcasting document events to connected clients.
"""
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
import logging

logger = logging.getLogger(__name__)


class DocumentNotificationConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for document notifications.
    
    Handles WebSocket connections and broadcasts document events
    (create, update) to all authenticated users in real-time.
    """
    
    async def connect(self):
        """
        Handle WebSocket connection.
        
        Authenticates the user and adds them to the notifications group.
        """
        # Get user from scope (set by AuthMiddleware)
        self.user = self.scope.get('user', AnonymousUser())
        
        # Only allow authenticated users
        if not self.user or not self.user.is_authenticated:
            logger.warning("Unauthenticated WebSocket connection attempt")
            await self.close()
            return
        
        # Group name for broadcasting
        self.room_group_name = 'document_notifications'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Accept connection
        await self.accept()
        
        logger.info(f"User {self.user.username} connected to WebSocket")
        
        # Send connection confirmation
        await self.send_json({
            'type': 'connection.established',
            'message': 'Connected to document notifications',
            'user': self.user.username
        })
    
    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection.
        
        Args:
            close_code: WebSocket close code
        """
        if hasattr(self, 'room_group_name'):
            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            
            if hasattr(self, 'user'):
                logger.info(
                    f"User {self.user.username} disconnected from WebSocket "
                    f"(code: {close_code})"
                )
    
    async def receive_json(self, content, **kwargs):
        """
        Handle messages received from WebSocket.
        
        Args:
            content: JSON content from client
        """
        # Echo back for testing/heartbeat
        message_type = content.get('type', 'unknown')
        
        if message_type == 'ping':
            await self.send_json({
                'type': 'pong',
                'timestamp': content.get('timestamp')
            })
    
    async def document_notification(self, event):
        """
        Handle document notification events from the channel layer.
        
        This method is called when a document event is broadcast to the group.
        
        Args:
            event: Event dictionary with notification data
        """
        # Send notification to WebSocket
        await self.send_json({
            'type': 'document.notification',
            'event': event.get('event_type'),
            'document': event.get('document'),
            'user': event.get('user'),
            'timestamp': event.get('timestamp')
        })

