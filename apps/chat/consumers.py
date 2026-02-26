"""
WebSocket consumer for real-time chat functionality.

This module implements the ChatConsumer class that handles WebSocket connections,
authentication, message routing, and channel layer group management for real-time
chat between users.
"""

import json
import logging
import nh3
import time

from apps.chat.models import Conversation, Message
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from redis.asyncio import Redis as AsyncRedis

User = get_user_model()
logger = logging.getLogger(__name__)

# Rate limiting configuration
RATE_LIMIT_MESSAGES = 10  # Maximum messages
RATE_LIMIT_WINDOW = 60  # Time window in seconds (1 minute)


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

        # Cache conversation object to avoid redundant DB queries in receive()
        self.conversation = await self.get_conversation()
        # Validate conversation exists (should always be true after participant check)
        if not self.conversation:
            # Close connection if conversation disappeared between checks
            await self.close(code=4004)
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
        2. Extracts message type (defaults to "chat_message" for backward compatibility)
        3. Dispatches to appropriate handler based on type
        4. Handles JSON parsing errors and unexpected exceptions

        Args:
            text_data: JSON string containing message data

        Expected JSON format:
        {
            "type": "chat_message",  # Optional, defaults to "chat_message"
            "message": "message content"
        }

        Supported message types:
        - "ping": Health check, responds with "pong"
        - "chat_message": Standard chat message (default)
        - Other types: Returns error for unknown types

        Requirements: 2.2, 3.1, 3.4, 9.1, 9.2, 9.3, 9.4, 9.5
        """
        try:
            # Parse incoming JSON data
            text_data_json = json.loads(text_data)

            # Extract message type, defaulting to "chat_message" for backward compatibility
            msg_type = text_data_json.get("type", "chat_message")

            # Dispatch to appropriate handler based on message type
            await self._dispatch(msg_type, text_data_json)

        except json.JSONDecodeError:
            # Invalid JSON format - send error to client
            await self._send_error("Invalid message format")
        except Exception as exc:
            # Unexpected error - log and send generic error to client
            logger.exception("Unexpected error in receive(): %s", exc)
            await self._send_error("An error occurred while processing your message")

    async def _dispatch(self, msg_type: str, data: dict):
        """
        Route incoming messages to appropriate handlers based on type.

        This method implements the message type protocol, allowing extensibility
        for future features like typing indicators and read receipts.

        Args:
            msg_type: The message type string (e.g., "ping", "chat_message")
            data: The full parsed JSON message data

        Supported types:
        - "ping": Responds with pong for connection health checks
        - "chat_message": Processes and broadcasts chat messages
        - Unknown types: Returns error message
        """
        # Handle ping messages for connection health checks
        if msg_type == "ping":
            # Send pong response immediately and return
            await self.send(text_data=json.dumps({"type": "pong"}))
            return

        # Handle standard chat messages (existing logic)
        elif msg_type == "chat_message":
            # Extract and validate message content
            message_content = data.get("message", "").strip()

            # Validate message content is not empty (Requirement 9.1)
            if not message_content:
                await self._send_error("Message content cannot be empty")
                return

            # Validate message length <= 5000 characters (Requirement 9.2)
            if len(message_content) > 5000:
                await self._send_error(
                    "Message exceeds maximum length of 5000 characters"
                )
                return

            # Check rate limiting (Requirement 9.4)
            is_allowed, cooldown_seconds = await self.check_rate_limit()
            if not is_allowed:
                # Send rate limit error with cooldown information
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
            sanitized_content = nh3.clean(
                message_content,
                tags=set(),  # Strip all HTML tags
            )

            # Validate sender and recipient are different users (Requirement 9.5)
            recipient_id = await self.get_recipient_id()
            if recipient_id == self.user.id:
                await self._send_error("Cannot send messages to yourself")
                return

            # Save message to database before broadcasting
            message = await self.save_message(sanitized_content)

            if message is None:
                # Database save failed - send error to client
                await self._send_error("Failed to save message")
                return

            # Broadcast message to room group after successful save
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

        # Handle unknown message types
        else:
            # Send error for unrecognized message types
            await self._send_error("Unknown message type")

    async def _send_error(self, message: str):
        """
        Send error message to WebSocket client.

        This helper method provides a consistent way to send error responses,
        reducing code duplication and ensuring uniform error message format.

        Args:
            message: Human-readable error message to send to client
        """
        # Send standardized error response to client
        await self.send(text_data=json.dumps({"type": "error", "message": message}))

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
    def get_conversation(self):
        """
        Fetch and return the conversation object by ID.

        This method retrieves the conversation once during connect() to avoid
        redundant database queries in subsequent operations.

        Returns:
            Conversation: The conversation object, or None if not found

        Requirements: Performance optimization
        """
        try:
            # Fetch conversation by ID to cache for later use
            return Conversation.objects.get(id=self.conversation_id)
        except Conversation.DoesNotExist:
            # Return None if conversation doesn't exist
            return None

    @database_sync_to_async
    def get_recipient_id(self):
        """
        Get the recipient user ID for the conversation.

        Returns the ID of the other participant (not the current user).
        Uses cached self.conversation to avoid redundant database query.

        Returns:
            int: The recipient's user ID, or None if conversation not found

        Requirements: 9.5
        """
        # Use cached conversation instead of querying DB again
        if not self.conversation:
            # Return None if conversation is not cached (shouldn't happen)
            return None

        # Return the participant who is NOT the current user
        if self.conversation.participant_one_id == self.user.id:
            return self.conversation.participant_two_id
        else:
            return self.conversation.participant_one_id

    @database_sync_to_async
    def save_message(self, content):
        """
        Save message to database before broadcasting.

        This method persists the message to PostgreSQL before delivery,
        ensuring message integrity and enabling conversation history.
        Uses cached self.conversation to avoid redundant database query.

        Args:
            content: Message content string (already validated and sanitized)

        Returns:
            Message: The created message object, or None if save failed

        Requirements: 3.1, 3.4
        """
        try:
            # Use cached conversation instead of querying DB again
            if not self.conversation:
                # Return None if conversation is not cached (shouldn't happen)
                logger.info("Conversation not cached")
                return None

            # Create message using the cached conversation object
            message = Message.objects.create(
                conversation=self.conversation, sender=self.user, content=content
            )
            return message
        except Exception as exc:
            # Database error - log and return None to trigger error response
            # In production, this should use proper logging
            logger.exception(
                "Failed to save message for conversation %s: %s",
                self.conversation_id,
                exc,
            )
            return None

    # Using Redis as a sliding window counter (async)
    async def check_rate_limit(self) -> tuple[bool, int]:
        """
        Sliding window rate limiter backed by Redis sorted sets.

        WHY Redis sorted sets?
        - Score = timestamp → lets us efficiently drop entries outside the window
        using ZREMRANGEBYSCORE in O(log N)
        - Atomic pipeline → all commands execute as a single round-trip, preventing
        race conditions between concurrent WebSocket workers

        WHY async?
        - This consumer is fully async; a sync call here would block the event loop
        and degrade performance for all concurrent connections on this worker

        Returns:
            tuple[bool, int]: (is_allowed, cooldown_seconds)
                is_allowed      → True if the message may proceed
                cooldown_seconds → seconds until the rate limit window resets (0 if allowed)

        Requirements: 9.4
        """
        current_time = time.time()

        # Unique Redis key per user — isolates each user's sliding window
        key = f"rate_limit:chat:{self.user.id}"

        # Cutoff timestamp — entries older than this are outside the window
        window_start = current_time - RATE_LIMIT_WINDOW

        # WHY from_url inside the method?
        # redis-py's async client is connection-pooled by default when reused;
        # using Django's cache or a module-level pool would be cleaner in production
        # (see improvement note below), but this is correct and safe for now.
        async with AsyncRedis.from_url(
            settings.REDIS_URL, decode_responses=True
        ) as redis:
            async with redis.pipeline(transaction=True) as pipe:
                # Step 1: remove timestamps that have fallen outside the sliding window
                pipe.zremrangebyscore(key, 0, window_start)

                # Step 2: record this attempt with its timestamp as both member and score
                pipe.zadd(key, {str(current_time): current_time})

                # Step 3: count how many messages are now inside the window
                pipe.zcard(key)

                # Step 4: ensure the key expires so Redis doesn't accumulate stale keys
                # for users who stop sending messages
                pipe.expire(key, RATE_LIMIT_WINDOW)

                # Execute all four commands atomically in one round-trip
                _, _, message_count, _ = await pipe.execute()

        # User is within the allowed limit — proceed normally
        if message_count <= RATE_LIMIT_MESSAGES:
            return True, 0

        # WHY fetch the oldest entry separately (outside the pipeline)?
        # We only reach here on the rare rate-limited path, so the extra
        # round-trip only happens when we're about to reject the message anyway.
        async with AsyncRedis.from_url(
            settings.REDIS_URL, decode_responses=True
        ) as redis:
            oldest = await redis.zrange(key, 0, 0, withscores=True)

        if oldest:
            # Calculate how many seconds until the oldest entry falls outside the window
            oldest_timestamp = oldest[0][1]
            cooldown_seconds = (
                int(oldest_timestamp + RATE_LIMIT_WINDOW - current_time) + 1
            )
        else:
            # Fallback — should not happen, but safe default
            cooldown_seconds = RATE_LIMIT_WINDOW

        return False, cooldown_seconds
