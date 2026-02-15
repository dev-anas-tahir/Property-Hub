"""
WebSocket consumer for real-time chat functionality.

This module implements the ChatConsumer class that handles WebSocket connections,
authentication, message routing, and channel layer group management for real-time
chat between users.
"""

import json
import bleach
import time
from collections import defaultdict
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Conversation, Message

User = get_user_model()

# Rate limiting configuration
RATE_LIMIT_MESSAGES = 10  # Maximum messages
RATE_LIMIT_WINDOW = 60  # Time window in seconds (1 minute)

# In-memory rate limiting storage (user_id -> list of timestamps)
# In production, this should use Redis for distributed rate limiting
rate_limit_storage = defaultdict(list)


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Handles WebSocket connections for real-time chat.

    This consumer manages:
    - User authentication and authorization
    - WebSocket connection lifecycle (connect/disconnect)
    - Incoming message handling and validation
    - Message broadcasting through channel layer groups
    - Real-time message delivery to connected clients

    Requirements: 1.4, 1.5, 2.2, 8.3
    """

    async def connect(self):
        """
        Authenticate user and join conversation room.

        This method:
        1. Verifies user authentication
        2. Extracts conversation_id from URL
        3. Validates user is participant in conversation
        4. Joins channel layer group for the conversation

        If authentication or authorization fails, the connection is rejected.

        Requirements: 1.4, 1.5, 8.3
        """
        # Extract conversation_id from URL route
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.room_group_name = f"chat_{self.conversation_id}"

        # Get user from scope (set by AuthMiddleware)
        self.user = self.scope.get("user")

        # Check if user is authenticated
        if not self.user or not self.user.is_authenticated:
            # Reject connection for unauthenticated users
            await self.close(code=4001)
            return

        # Verify user is a participant in this conversation
        is_participant = await self.check_user_is_participant()
        if not is_participant:
            # Reject connection if user is not a participant
            await self.close(code=4003)
            return

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # Accept the WebSocket connection
        await self.accept()

        # Note: Unread messages are already loaded in the template on page load
        # No need to send them again via WebSocket to avoid duplication

    async def disconnect(self, close_code):
        """
        Clean up when WebSocket closes.

        This method:
        1. Leaves the channel layer group
        2. Logs disconnection for debugging

        Args:
            close_code: WebSocket close code indicating reason for disconnection

        Requirements: 8.3
        """
        # Leave room group
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )

    async def receive(self, text_data):
        """
        Handle incoming messages from WebSocket.

        This method:
        1. Parses JSON message from client
        2. Validates message content (not empty, length <= 5000, sanitizes XSS)
        3. Validates sender and recipient are different users
        4. Checks rate limiting (10 messages per minute)
        5. Saves message to database before broadcasting
        6. Handles database errors and returns error to sender
        7. Broadcasts message through channel layer after successful save

        Args:
            text_data: JSON string containing message data

        Expected JSON format:
        {
            "message": "message content"
        }

        Requirements: 2.2, 3.1, 3.4, 9.1, 9.2, 9.3, 9.4, 9.5
        """
        try:
            # Parse incoming JSON data
            text_data_json = json.loads(text_data)
            message_content = text_data_json.get("message", "").strip()

            # Validate message content is not empty (Requirement 9.1)
            if not message_content:
                await self.send(
                    text_data=json.dumps(
                        {"type": "error", "message": "Message content cannot be empty"}
                    )
                )
                return

            # Validate message length <= 5000 characters (Requirement 9.2)
            if len(message_content) > 5000:
                await self.send(
                    text_data=json.dumps(
                        {
                            "type": "error",
                            "message": "Message exceeds maximum length of 5000 characters",
                        }
                    )
                )
                return

            # Check rate limiting (Requirement 9.4)
            is_allowed, cooldown_seconds = self.check_rate_limit()
            if not is_allowed:
                await self.send(
                    text_data=json.dumps(
                        {
                            "type": "rate_limit_error",
                            "message": f"Rate limit exceeded. Please wait {cooldown_seconds} seconds before sending another message.",
                            "cooldown_seconds": cooldown_seconds,
                            "status_code": 429,
                        }
                    )
                )
                return

            # Sanitize message content for XSS prevention (Requirement 9.3)
            sanitized_content = bleach.clean(
                message_content,
                tags=[],  # Strip all HTML tags
                strip=True,
            )

            # Validate sender and recipient are different users (Requirement 9.5)
            recipient_id = await self.get_recipient_id()
            if recipient_id == self.user.id:
                await self.send(
                    text_data=json.dumps(
                        {"type": "error", "message": "Cannot send messages to yourself"}
                    )
                )
                return

            # Save message to database
            message = await self.save_message(sanitized_content)

            if message is None:
                # Database save failed
                await self.send(
                    text_data=json.dumps(
                        {"type": "error", "message": "Failed to save message"}
                    )
                )
                return

            # Broadcast message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": sanitized_content,
                    "sender_id": self.user.id,
                    "sender_email": self.user.email,
                    "message_id": message.id,
                    "created_at": message.created_at.isoformat(),
                },
            )

        except json.JSONDecodeError:
            # Invalid JSON format
            await self.send(
                text_data=json.dumps(
                    {"type": "error", "message": "Invalid message format"}
                )
            )
        except Exception:
            # Unexpected error
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "error",
                        "message": "An error occurred while processing your message",
                    }
                )
            )

    async def chat_message(self, event):
        """
        Send message to WebSocket client.

        This method receives messages from the channel layer and sends them
        to the WebSocket client. It's called when a message is broadcast
        to the conversation group.

        Args:
            event: Dictionary containing message data from channel layer

        Expected event format:
        {
            'type': 'chat_message',
            'message': 'message content',
            'sender_id': 123,
            'sender_email': 'user@example.com',
            'message_id': 456,
            'created_at': '2024-01-01T12:00:00'
        }

        Requirements: 2.2
        """
        # Send message to WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "type": "message",
                    "message": event["message"],
                    "sender_id": event["sender_id"],
                    "sender_email": event["sender_email"],
                    "message_id": event["message_id"],
                    "created_at": event["created_at"],
                }
            )
        )

    @database_sync_to_async
    def check_user_is_participant(self):
        """
        Check if the current user is a participant in the conversation.

        Returns:
            bool: True if user is participant_one or participant_two, False otherwise

        Requirements: 1.4, 1.5
        """
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            return (
                conversation.participant_one_id == self.user.id
                or conversation.participant_two_id == self.user.id
            )
        except Conversation.DoesNotExist:
            return False

    @database_sync_to_async
    def get_recipient_id(self):
        """
        Get the recipient user ID for the conversation.

        Returns the ID of the other participant (not the current user).

        Returns:
            int: The recipient's user ID, or None if conversation not found

        Requirements: 9.5
        """
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            if conversation.participant_one_id == self.user.id:
                return conversation.participant_two_id
            else:
                return conversation.participant_one_id
        except Conversation.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message(self, content):
        """
        Save message to database before broadcasting.

        This method persists the message to PostgreSQL before delivery,
        ensuring message integrity and enabling conversation history.

        Args:
            content: Message content string (already validated and sanitized)

        Returns:
            Message: The created message object, or None if save failed

        Requirements: 3.1, 3.4
        """
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            message = Message.objects.create(
                conversation=conversation, sender=self.user, content=content
            )
            return message
        except Conversation.DoesNotExist:
            # Conversation not found - should not happen if connection was validated
            return None
        except Exception:
            # Database error - log and return None to trigger error response
            # In production, this should use proper logging
            return None

    def check_rate_limit(self):
        """
        Check if the user has exceeded the rate limit for sending messages.

        Implements a sliding window rate limiter that allows RATE_LIMIT_MESSAGES
        messages per RATE_LIMIT_WINDOW seconds.

        Returns:
            tuple: (is_allowed: bool, cooldown_seconds: int)
                - is_allowed: True if user can send message, False if rate limited
                - cooldown_seconds: Seconds until user can send next message (0 if allowed)

        Requirements: 9.4
        """
        current_time = time.time()
        user_id = self.user.id

        # Get user's message timestamps
        timestamps = rate_limit_storage[user_id]

        # Remove timestamps outside the current window
        cutoff_time = current_time - RATE_LIMIT_WINDOW
        timestamps[:] = [ts for ts in timestamps if ts > cutoff_time]

        # Check if user has exceeded the limit
        if len(timestamps) >= RATE_LIMIT_MESSAGES:
            # Calculate cooldown time (time until oldest message expires from window)
            oldest_timestamp = timestamps[0]
            cooldown_seconds = (
                int(oldest_timestamp + RATE_LIMIT_WINDOW - current_time) + 1
            )
            return False, cooldown_seconds

        # User is within rate limit, add current timestamp
        timestamps.append(current_time)
        return True, 0
