"""
WebSocket URL routing configuration for Django Channels.

This module defines the WebSocket URL patterns that will be used
by the ASGI application to route WebSocket connections.
"""

from django.urls import path
from apps.chat.consumers import ChatConsumer

# WebSocket URL patterns for real-time chat
websocket_urlpatterns = [
    path("ws/chat/<int:conversation_id>/", ChatConsumer.as_asgi()),
]
