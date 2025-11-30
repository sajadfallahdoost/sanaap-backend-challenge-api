"""
WebSocket URL routing for document notifications.

This module defines WebSocket URL patterns for Django Channels.
"""
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/documents/notifications/', consumers.DocumentNotificationConsumer.as_asgi()),
]

