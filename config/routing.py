"""
WebSocket URL routing configuration for Django Channels.

This module defines the WebSocket URL patterns that will be used
by the ASGI application to route WebSocket connections.
"""

from django.urls import path


def get_websocket_urlpatterns():
    """
    Lazy load websocket URL patterns to avoid importing models before Django apps are ready.
    """
    from apps.chat.consumers import ChatConsumer

    return [
        path("ws/chat/<int:conversation_id>/", ChatConsumer.as_asgi()),
    ]


# This will be evaluated when accessed, not at import time
websocket_urlpatterns = []
