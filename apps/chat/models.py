"""
Models for the real-time chat feature.
"""

from django.conf import settings
from django.db import models


class Conversation(models.Model):
    """
    Represents a chat conversation between two users about a property.

    Ensures only one conversation exists between any two users for a specific property
    through the unique_together constraint.
    """

    property = models.ForeignKey(
        "properties.Property", on_delete=models.CASCADE, related_name="conversations"
    )
    participant_one = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversations_as_p1",
    )
    participant_two = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversations_as_p2",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("property", "participant_one", "participant_two")
        indexes = [
            models.Index(fields=["participant_one", "updated_at"]),
            models.Index(fields=["participant_two", "updated_at"]),
        ]
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Conversation {self.id}: {self.participant_one} & {self.participant_two} about {self.property}"


class Message(models.Model):
    """
    Represents a single message in a conversation.

    Messages are ordered chronologically and include read status tracking
    for unread message indicators.
    """

    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages"
    )
    content = models.TextField(max_length=5000)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["conversation", "created_at"]),
            models.Index(fields=["conversation", "is_read"]),
        ]
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"Message {self.id} from {self.sender}: {preview}"
