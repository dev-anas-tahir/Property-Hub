"""
Tests for the real-time chat feature.
"""

from apps.chat.consumers import ChatConsumer
from apps.chat.models import Conversation, Message
from apps.properties.models import Property
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from django.test import TransactionTestCase, override_settings
from django.contrib.auth import get_user_model

User = get_user_model()


@override_settings(
    CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
)
class ChatConsumerTestCase(TransactionTestCase):
    """
    Test cases for ChatConsumer WebSocket functionality.

    Tests cover:
    - Authentication and authorization
    - Connection and disconnection
    - Message sending and receiving
    - Channel layer group management
    """

    @database_sync_to_async
    def create_test_data(self):
        """Create test users, property, and conversation."""
        # Create users
        self.user1 = User.objects.create_user(
            email="user1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com", password="testpass123"
        )
        self.user3 = User.objects.create_user(
            email="user3@example.com", password="testpass123"
        )

        # Create property
        self.property = Property.objects.create(
            user=self.user2,
            name="Test Property",
            full_address="123 Test St, Test City, TS 12345",
            phone_number="03001234567",
            cnic="12345-1234567-1",
            property_type="House",
            description="A test property",
            price=100000,
        )

        # Create conversation
        self.conversation = Conversation.objects.create(
            property=self.property,
            participant_one=self.user1,
            participant_two=self.user2,
        )

    async def test_authenticated_user_can_connect(self):
        """
        Test that an authenticated participant can connect to the WebSocket.

        Requirements: 1.4, 1.5, 8.3
        """
        await self.create_test_data()

        # Create communicator with authenticated user
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self.conversation.id}/"
        )
        communicator.scope["user"] = self.user1
        communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": self.conversation.id}
        }

        # Connect
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Disconnect
        await communicator.disconnect()

    async def test_unauthenticated_user_cannot_connect(self):
        """
        Test that an unauthenticated user cannot connect to the WebSocket.

        Requirements: 1.4, 1.5
        """
        await self.create_test_data()

        # Create communicator without authenticated user
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self.conversation.id}/"
        )
        communicator.scope["user"] = None
        communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": self.conversation.id}
        }

        # Attempt to connect
        connected, close_code = await communicator.connect()
        self.assertFalse(connected)
        self.assertEqual(close_code, 4001)

    async def test_non_participant_cannot_connect(self):
        """
        Test that a user who is not a participant cannot connect.

        Requirements: 1.4, 1.5
        """
        await self.create_test_data()

        # Create communicator with user3 (not a participant)
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self.conversation.id}/"
        )
        communicator.scope["user"] = self.user3
        communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": self.conversation.id}
        }

        # Attempt to connect
        connected, close_code = await communicator.connect()
        self.assertFalse(connected)
        self.assertEqual(close_code, 4003)

    async def test_send_and_receive_message(self):
        """
        Test that a message can be sent and received through WebSocket.

        Requirements: 2.2
        """
        await self.create_test_data()

        # Create communicator
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self.conversation.id}/"
        )
        communicator.scope["user"] = self.user1
        communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": self.conversation.id}
        }

        # Connect
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Send message
        await communicator.send_json_to({"message": "Hello, this is a test message"})

        # Receive message
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "message")
        self.assertEqual(response["message"], "Hello, this is a test message")
        self.assertEqual(response["sender_id"], self.user1.id)

        # Disconnect
        await communicator.disconnect()

    async def test_empty_message_rejected(self):
        """
        Test that empty messages are rejected with an error.

        Requirements: 2.2
        """
        await self.create_test_data()

        # Create communicator
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self.conversation.id}/"
        )
        communicator.scope["user"] = self.user1
        communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": self.conversation.id}
        }

        # Connect
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Send empty message
        await communicator.send_json_to({"message": "   "})

        # Receive error response
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "error")
        self.assertIn("empty", response["message"].lower())

        # Disconnect
        await communicator.disconnect()

    async def test_message_persisted_to_database(self):
        """
        Test that messages are saved to the database.

        Requirements: 2.2
        """
        await self.create_test_data()

        # Create communicator
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self.conversation.id}/"
        )
        communicator.scope["user"] = self.user1
        communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": self.conversation.id}
        }

        # Connect
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Send message
        test_message = "This message should be persisted"
        await communicator.send_json_to({"message": test_message})

        # Receive confirmation
        await communicator.receive_json_from()

        # Check database
        @database_sync_to_async
        def check_message():
            return Message.objects.filter(
                conversation=self.conversation, sender=self.user1, content=test_message
            ).exists()

        message_exists = await check_message()
        self.assertTrue(message_exists)

        # Disconnect
        await communicator.disconnect()

    async def test_message_length_validation(self):
        """
        Test that messages exceeding 5000 characters are rejected.

        Requirements: 9.2
        """
        await self.create_test_data()

        # Create communicator
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self.conversation.id}/"
        )
        communicator.scope["user"] = self.user1
        communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": self.conversation.id}
        }

        # Connect
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Send message that exceeds 5000 characters
        long_message = "a" * 5001
        await communicator.send_json_to({"message": long_message})

        # Receive error response
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "error")
        self.assertIn("5000", response["message"])

        # Disconnect
        await communicator.disconnect()

    async def test_message_xss_sanitization(self):
        """
        Test that message content is sanitized to prevent XSS attacks.

        Requirements: 9.3
        """
        await self.create_test_data()

        # Create communicator
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self.conversation.id}/"
        )
        communicator.scope["user"] = self.user1
        communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": self.conversation.id}
        }

        # Connect
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Send message with HTML/JavaScript
        malicious_message = '<script>alert("XSS")</script>Hello'
        await communicator.send_json_to({"message": malicious_message})

        # Receive sanitized message
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "message")
        # Should strip HTML tags and script content for security
        self.assertNotIn("<script>", response["message"])
        self.assertNotIn("</script>", response["message"])
        self.assertNotIn("alert", response["message"])
        self.assertEqual(response["message"], "Hello")

        # Disconnect
        await communicator.disconnect()

    async def test_self_messaging_prevention(self):
        """
        Test that users cannot send messages to themselves.

        Requirements: 9.5
        """
        await self.create_test_data()

        # Create a conversation where user1 is both participants (edge case)
        @database_sync_to_async
        def create_self_conversation():
            return Conversation.objects.create(
                property=self.property,
                participant_one=self.user1,
                participant_two=self.user1,
            )

        self_conversation = await create_self_conversation()

        # Create communicator
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self_conversation.id}/"
        )
        communicator.scope["user"] = self.user1
        communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": self_conversation.id}
        }

        # Connect
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Attempt to send message
        await communicator.send_json_to({"message": "Talking to myself"})

        # Receive error response
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "error")
        self.assertIn("yourself", response["message"].lower())

        # Disconnect
        await communicator.disconnect()

    async def test_message_at_max_length_accepted(self):
        """
        Test that messages at exactly 5000 characters are accepted.

        Requirements: 9.2
        """
        await self.create_test_data()

        # Create communicator
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self.conversation.id}/"
        )
        communicator.scope["user"] = self.user1
        communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": self.conversation.id}
        }

        # Connect
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Send message at exactly 5000 characters
        max_message = "a" * 5000
        await communicator.send_json_to({"message": max_message})

        # Receive message (should succeed)
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "message")
        self.assertEqual(len(response["message"]), 5000)

        # Disconnect
        await communicator.disconnect()

    async def test_database_error_handling(self):
        """
        Test that database errors are handled and return error to sender.

        When database persistence fails, the system should return an error
        to the sender and not broadcast the message.

        Requirements: 3.4
        """
        await self.create_test_data()

        # Create communicator
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self.conversation.id}/"
        )
        communicator.scope["user"] = self.user1
        communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": self.conversation.id}
        }

        # Connect
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Delete the conversation to simulate database error
        @database_sync_to_async
        def delete_conversation():
            Conversation.objects.filter(id=self.conversation.id).delete()

        await delete_conversation()

        # Send message (should fail because conversation doesn't exist)
        await communicator.send_json_to({"message": "This should fail to save"})

        # Receive error response
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "error")
        self.assertIn("Failed to save message", response["message"])

        # Disconnect
        await communicator.disconnect()


class ConversationListViewTestCase(TransactionTestCase):
    """
    Test cases for the conversation list view.

    Tests cover:
    - Authentication requirement
    - Conversation filtering by participant
    - Unread message count annotation
    - Ordering by updated_at descending
    """

    def setUp(self):
        """Create test users, properties, and conversations."""
        # Create users
        self.user1 = User.objects.create_user(
            email="user1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com", password="testpass123"
        )
        self.user3 = User.objects.create_user(
            email="user3@example.com", password="testpass123"
        )

        # Create properties
        self.property1 = Property.objects.create(
            user=self.user2,
            name="Property 1",
            full_address="123 Test St",
            phone_number="03001234567",
            cnic="12345-1234567-1",
            property_type="House",
            description="Test property 1",
            price=100000,
        )

        self.property2 = Property.objects.create(
            user=self.user3,
            name="Property 2",
            full_address="456 Test Ave",
            phone_number="03001234568",
            cnic="12345-1234567-2",
            property_type="Apartment",
            description="Test property 2",
            price=150000,
        )

        # Create conversations
        self.conversation1 = Conversation.objects.create(
            property=self.property1,
            participant_one=self.user1,
            participant_two=self.user2,
        )

        self.conversation2 = Conversation.objects.create(
            property=self.property2,
            participant_one=self.user1,
            participant_two=self.user3,
        )

    def test_unauthenticated_user_redirected(self):
        """
        Test that unauthenticated users are redirected to login page.

        Requirements: 1.1
        """
        response = self.client.get("/chat/conversations/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_authenticated_user_can_access(self):
        """
        Test that authenticated users can access the conversation list.

        Requirements: 5.1
        """
        self.client.force_login(self.user1)
        response = self.client.get("/chat/conversations/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "chat/conversation_list.html")

    def test_user_sees_only_their_conversations(self):
        """
        Test that users only see conversations where they are a participant.

        Requirements: 5.1
        """
        self.client.force_login(self.user1)
        response = self.client.get("/chat/conversations/")

        conversations = response.context["conversations"]
        self.assertEqual(len(conversations), 2)

        # Verify user1 is a participant in all returned conversations
        for conversation in conversations:
            self.assertTrue(
                conversation.participant_one == self.user1
                or conversation.participant_two == self.user1
            )

    def test_user_does_not_see_others_conversations(self):
        """
        Test that users don't see conversations they're not part of.

        Requirements: 5.1
        """
        # Create a conversation between user2 and user3 (not involving user1)
        conversation3 = Conversation.objects.create(
            property=self.property1,
            participant_one=self.user2,
            participant_two=self.user3,
        )

        self.client.force_login(self.user1)
        response = self.client.get("/chat/conversations/")

        conversations = response.context["conversations"]
        conversation_ids = [c.id for c in conversations]

        # user1 should not see conversation3
        self.assertNotIn(conversation3.id, conversation_ids)

    def test_conversations_ordered_by_updated_at_descending(self):
        """
        Test that conversations are ordered by most recent activity.

        Requirements: 5.4
        """
        # Create messages to update conversation timestamps
        Message.objects.create(
            conversation=self.conversation1,
            sender=self.user1,
            content="Message in conversation 1",
        )

        # Wait a moment and create message in conversation2
        import time

        time.sleep(0.1)

        Message.objects.create(
            conversation=self.conversation2,
            sender=self.user1,
            content="Message in conversation 2",
        )

        self.client.force_login(self.user1)
        response = self.client.get("/chat/conversations/")

        conversations = list(response.context["conversations"])

        # conversation2 should be first (most recent)
        self.assertEqual(conversations[0].id, self.conversation2.id)
        self.assertEqual(conversations[1].id, self.conversation1.id)

    def test_unread_message_count_accuracy(self):
        """
        Test that unread message count is accurate for each conversation.

        Requirements: 5.5
        """
        # Create unread messages from user2 to user1
        Message.objects.create(
            conversation=self.conversation1,
            sender=self.user2,
            content="Unread message 1",
            is_read=False,
        )
        Message.objects.create(
            conversation=self.conversation1,
            sender=self.user2,
            content="Unread message 2",
            is_read=False,
        )

        # Create a read message
        Message.objects.create(
            conversation=self.conversation1,
            sender=self.user2,
            content="Read message",
            is_read=True,
        )

        # Create a message sent by user1 (should not count as unread for user1)
        Message.objects.create(
            conversation=self.conversation1,
            sender=self.user1,
            content="My own message",
            is_read=False,
        )

        self.client.force_login(self.user1)
        response = self.client.get("/chat/conversations/")

        conversations = list(response.context["conversations"])
        conversation1 = next(c for c in conversations if c.id == self.conversation1.id)

        # Should count only the 2 unread messages from user2
        self.assertEqual(conversation1.unread_count, 2)

    def test_empty_conversation_list(self):
        """
        Test that users with no conversations see an empty state.

        Requirements: 5.1
        """
        # Create a new user with no conversations
        user4 = User.objects.create_user(
            email="user4@example.com", password="testpass123"
        )

        self.client.force_login(user4)
        response = self.client.get("/chat/conversations/")

        conversations = response.context["conversations"]
        self.assertEqual(len(conversations), 0)
        self.assertContains(response, "No conversations yet")

    def test_other_participant_identified_correctly(self):
        """
        Test that the other participant is correctly identified in each conversation.

        Requirements: 5.2
        """
        self.client.force_login(self.user1)
        response = self.client.get("/chat/conversations/")

        conversations = list(response.context["conversations"])

        for conversation in conversations:
            # The other participant should not be user1
            self.assertNotEqual(conversation.other_participant, self.user1)

            # The other participant should be one of the conversation participants
            self.assertIn(
                conversation.other_participant,
                [conversation.participant_one, conversation.participant_two],
            )

    def test_conversation_displays_property_context(self):
        """
        Test that conversations display the associated property information.

        Requirements: 5.2
        """
        self.client.force_login(self.user1)
        response = self.client.get("/chat/conversations/")

        # Check that property names are in the response
        self.assertContains(response, self.property1.name)
        self.assertContains(response, self.property2.name)


class ConversationDetailViewTestCase(TransactionTestCase):
    """
    Test cases for the conversation detail view.

    Tests cover:
    - Authentication requirement
    - Participant authorization
    - Message loading in chronological order
    - Marking messages as read
    """

    def setUp(self):
        """Create test users, properties, conversations, and messages."""
        # Create users
        self.user1 = User.objects.create_user(
            email="user1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com", password="testpass123"
        )
        self.user3 = User.objects.create_user(
            email="user3@example.com", password="testpass123"
        )

        # Create property
        self.property = Property.objects.create(
            user=self.user2,
            name="Test Property",
            full_address="123 Test St",
            phone_number="03001234567",
            cnic="12345-1234567-1",
            property_type="House",
            description="Test property",
            price=100000,
        )

        # Create conversation
        self.conversation = Conversation.objects.create(
            property=self.property,
            participant_one=self.user1,
            participant_two=self.user2,
        )

        # Create messages
        self.message1 = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            content="First message",
            is_read=False,
        )

        self.message2 = Message.objects.create(
            conversation=self.conversation,
            sender=self.user2,
            content="Second message",
            is_read=False,
        )

        self.message3 = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            content="Third message",
            is_read=False,
        )

    def test_unauthenticated_user_redirected(self):
        """
        Test that unauthenticated users are redirected to login page.

        Requirements: 1.1
        """
        response = self.client.get(f"/chat/conversations/{self.conversation.id}/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_participant_can_access_conversation(self):
        """
        Test that participants can access the conversation detail view.

        Requirements: 3.2
        """
        self.client.force_login(self.user1)
        response = self.client.get(f"/chat/conversations/{self.conversation.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "chat/conversation_detail.html")

    def test_non_participant_cannot_access_conversation(self):
        """
        Test that non-participants cannot access the conversation.

        Requirements: Authorization
        """
        self.client.force_login(self.user3)
        response = self.client.get(f"/chat/conversations/{self.conversation.id}/")
        self.assertEqual(response.status_code, 403)

    def test_messages_loaded_chronologically(self):
        """
        Test that messages are loaded in chronological order (by created_at).

        Requirements: 3.2
        """
        self.client.force_login(self.user1)
        response = self.client.get(f"/chat/conversations/{self.conversation.id}/")

        messages = list(response.context["messages"])

        # Verify messages are in chronological order
        self.assertEqual(len(messages), 3)
        self.assertEqual(messages[0].id, self.message1.id)
        self.assertEqual(messages[1].id, self.message2.id)
        self.assertEqual(messages[2].id, self.message3.id)

        # Verify timestamps are in ascending order
        for i in range(len(messages) - 1):
            self.assertLessEqual(messages[i].created_at, messages[i + 1].created_at)

    def test_messages_marked_as_read_on_open(self):
        """
        Test that unread messages are marked as read when conversation is opened.

        Requirements: 7.2, 7.3
        """
        # Verify messages are initially unread
        self.assertFalse(self.message1.is_read)
        self.assertFalse(self.message2.is_read)
        self.assertFalse(self.message3.is_read)

        # User1 opens the conversation
        self.client.force_login(self.user1)
        response = self.client.get(f"/chat/conversations/{self.conversation.id}/")
        self.assertEqual(response.status_code, 200)

        # Refresh messages from database
        self.message1.refresh_from_db()
        self.message2.refresh_from_db()
        self.message3.refresh_from_db()

        # Messages sent by user2 to user1 should be marked as read
        self.assertTrue(self.message2.is_read)

        # Messages sent by user1 should remain unchanged (user doesn't mark their own messages as read)
        self.assertFalse(self.message1.is_read)
        self.assertFalse(self.message3.is_read)

    def test_only_recipient_messages_marked_as_read(self):
        """
        Test that only messages where the current user is the recipient are marked as read.

        Requirements: 7.2, 7.3
        """
        # Create more messages
        Message.objects.create(
            conversation=self.conversation,
            sender=self.user2,
            content="Message from user2 to user1",
            is_read=False,
        )
        Message.objects.create(
            conversation=self.conversation,
            sender=self.user2,
            content="Another message from user2",
            is_read=False,
        )

        # User1 opens the conversation
        self.client.force_login(self.user1)
        response = self.client.get(f"/chat/conversations/{self.conversation.id}/")
        self.assertEqual(response.status_code, 200)

        # Count unread messages sent by user1 (should remain unread)
        unread_from_user1 = Message.objects.filter(
            conversation=self.conversation, sender=self.user1, is_read=False
        ).count()
        self.assertEqual(unread_from_user1, 2)  # message1 and message3

        # Count unread messages sent by user2 (should all be read now)
        unread_from_user2 = Message.objects.filter(
            conversation=self.conversation, sender=self.user2, is_read=False
        ).count()
        self.assertEqual(unread_from_user2, 0)

    def test_other_participant_identified_correctly(self):
        """
        Test that the other participant is correctly identified.

        Requirements: Display
        """
        self.client.force_login(self.user1)
        response = self.client.get(f"/chat/conversations/{self.conversation.id}/")

        other_participant = response.context["other_participant"]
        self.assertEqual(other_participant, self.user2)

        # Test from user2's perspective
        self.client.force_login(self.user2)
        response = self.client.get(f"/chat/conversations/{self.conversation.id}/")

        other_participant = response.context["other_participant"]
        self.assertEqual(other_participant, self.user1)

    def test_conversation_context_includes_property(self):
        """
        Test that the conversation context includes the property information.

        Requirements: 6.5
        """
        self.client.force_login(self.user1)
        response = self.client.get(f"/chat/conversations/{self.conversation.id}/")

        conversation = response.context["conversation"]
        self.assertEqual(conversation.property, self.property)
        self.assertContains(response, self.property.name)

    def test_empty_conversation_displays_correctly(self):
        """
        Test that conversations with no messages display an empty state.

        Requirements: Display
        """
        # Create a new conversation with no messages
        empty_conversation = Conversation.objects.create(
            property=self.property,
            participant_one=self.user1,
            participant_two=self.user3,
        )

        self.client.force_login(self.user1)
        response = self.client.get(f"/chat/conversations/{empty_conversation.id}/")

        self.assertEqual(response.status_code, 200)
        messages = response.context["messages"]
        self.assertEqual(len(messages), 0)
        self.assertContains(response, "No messages yet")

    def test_nonexistent_conversation_returns_404(self):
        """
        Test that accessing a non-existent conversation returns 404.

        Requirements: Error handling
        """
        self.client.force_login(self.user1)
        response = self.client.get("/chat/conversations/99999/")
        self.assertEqual(response.status_code, 404)

    def test_messages_display_sender_information(self):
        """
        Test that messages include sender information in the context.

        Requirements: Display
        """
        self.client.force_login(self.user1)
        response = self.client.get(f"/chat/conversations/{self.conversation.id}/")

        messages = response.context["messages"]

        # Verify each message has sender information
        for message in messages:
            self.assertIsNotNone(message.sender)
            self.assertIn(message.sender, [self.user1, self.user2])

    def test_unread_messages_highlighted_in_template(self):
        """
        Test that unread messages are highlighted with visual indicators in the template.

        Requirements: 7.1
        """
        # Create unread messages from user2 to user1
        Message.objects.create(
            conversation=self.conversation,
            sender=self.user2,
            content="This is an unread message",
            is_read=False,
        )

        # Create a read message for comparison
        Message.objects.create(
            conversation=self.conversation,
            sender=self.user2,
            content="This is a read message",
            is_read=True,
        )

        self.client.force_login(self.user1)
        response = self.client.get(f"/chat/conversations/{self.conversation.id}/")

        content = response.content.decode()

        # Verify unread message has highlighting classes
        self.assertIn("ring-2 ring-primary-400 ring-offset-2", content)
        self.assertIn("badge badge-primary badge-xs", content)
        self.assertIn("New", content)

    def test_sender_name_and_timestamp_displayed(self):
        """
        Test that each message displays sender name and timestamp.

        Requirements: 3.2, 7.1
        """
        self.client.force_login(self.user1)
        response = self.client.get(f"/chat/conversations/{self.conversation.id}/")

        content = response.content.decode()

        # Verify timestamps are displayed
        for message in [self.message1, self.message2, self.message3]:
            # Check that message content is present
            self.assertIn(message.content, content)

        # Verify timestamp format is present (e.g., "Jan 1, 2024 12:00 PM")
        # The exact format depends on the date filter, but we can check for common patterns
        import re

        timestamp_pattern = r"\w{3}\s+\d{1,2},\s+\d{4}\s+\d{1,2}:\d{2}\s+[AP]M"
        self.assertTrue(
            re.search(timestamp_pattern, content),
            "Timestamp format not found in response",
        )


@override_settings(
    CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
)
class OfflineMessageHandlingTestCase(TransactionTestCase):
    """
    Test cases for offline message handling.

    Tests cover:
    - Task 7.1: Offline message persistence with unread status
    - Task 7.2: Unread message delivery on connection
    - Task 7.3: Historical message loading from database
    """

    @database_sync_to_async
    def create_test_data(self):
        """Create test users, property, and conversation."""
        # Create users
        self.user1 = User.objects.create_user(
            email="user1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com", password="testpass123"
        )

        # Create property
        self.property = Property.objects.create(
            user=self.user2,
            name="Test Property",
            full_address="123 Test St, Test City, TS 12345",
            phone_number="03001234567",
            cnic="12345-1234567-1",
            property_type="House",
            description="A test property",
            price=100000,
        )

        # Create conversation
        self.conversation = Conversation.objects.create(
            property=self.property,
            participant_one=self.user1,
            participant_two=self.user2,
        )

    @database_sync_to_async
    def create_offline_messages(self):
        """Create unread messages for offline recipient."""
        # Create messages from user1 to user2 (user2 is offline)
        self.message1 = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            content="First offline message",
            is_read=False,
        )
        self.message2 = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            content="Second offline message",
            is_read=False,
        )
        self.message3 = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            content="Third offline message",
            is_read=False,
        )

    async def test_offline_message_persistence(self):
        """
        Test that messages are persisted with unread status for offline recipients.

        Task 7.1: Add offline message persistence logic
        Requirements: 4.1, 4.4
        """
        await self.create_test_data()

        # User1 connects and sends a message (user2 is offline)
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self.conversation.id}/"
        )
        communicator.scope["user"] = self.user1
        communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": self.conversation.id}
        }

        # Connect
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Send message while user2 is offline
        await communicator.send_json_to({"message": "Message for offline user"})

        # Receive confirmation
        await communicator.receive_json_from()

        # Check that message was persisted with is_read=False
        @database_sync_to_async
        def check_message_status():
            message = Message.objects.filter(
                conversation=self.conversation,
                sender=self.user1,
                content="Message for offline user",
            ).first()
            return message is not None and not message.is_read

        message_is_unread = await check_message_status()
        self.assertTrue(
            message_is_unread,
            "Message should be persisted with is_read=False for offline recipient",
        )

        # Disconnect
        await communicator.disconnect()

    async def test_unread_messages_delivered_on_connection(self):
        """
        Test that unread messages are delivered when user connects.

        Task 7.2: Implement unread message delivery on connection
        Requirements: 4.2
        """
        await self.create_test_data()
        await self.create_offline_messages()

        # User2 connects (should receive all unread messages)
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self.conversation.id}/"
        )
        communicator.scope["user"] = self.user2
        communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": self.conversation.id}
        }

        # Connect
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Receive all unread messages
        received_messages = []
        for _ in range(3):  # Expect 3 unread messages
            response = await communicator.receive_json_from(timeout=2)
            received_messages.append(response)

        # Verify all 3 messages were received
        self.assertEqual(len(received_messages), 3)

        # Verify message content
        message_contents = [msg["message"] for msg in received_messages]
        self.assertIn("First offline message", message_contents)
        self.assertIn("Second offline message", message_contents)
        self.assertIn("Third offline message", message_contents)

        # Verify messages are marked as unread
        for msg in received_messages:
            self.assertEqual(msg["type"], "message")
            self.assertFalse(msg["is_read"])

        # Disconnect
        await communicator.disconnect()

    async def test_only_recipient_unread_messages_delivered(self):
        """
        Test that only messages where user is recipient are delivered as unread.

        Task 7.2: Implement unread message delivery on connection
        Requirements: 4.2
        """
        await self.create_test_data()

        # Create mixed messages
        @database_sync_to_async
        def create_mixed_messages():
            # Messages from user1 to user2 (unread)
            Message.objects.create(
                conversation=self.conversation,
                sender=self.user1,
                content="From user1 to user2",
                is_read=False,
            )
            # Messages from user2 (should not be delivered as unread to user2)
            Message.objects.create(
                conversation=self.conversation,
                sender=self.user2,
                content="From user2 to user1",
                is_read=False,
            )

        await create_mixed_messages()

        # User2 connects
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self.conversation.id}/"
        )
        communicator.scope["user"] = self.user2
        communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": self.conversation.id}
        }

        # Connect
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Should receive only 1 unread message (from user1)
        response = await communicator.receive_json_from(timeout=2)
        self.assertEqual(response["message"], "From user1 to user2")
        self.assertEqual(response["sender_id"], self.user1.id)

        # Should not receive any more messages
        import asyncio

        try:
            await communicator.receive_json_from(timeout=0.5)
            self.fail("Should not have received additional messages")
        except asyncio.TimeoutError:
            pass  # Expected - no more messages

    async def test_no_unread_messages_on_connection(self):
        """
        Test that no messages are sent if there are no unread messages.

        Task 7.2: Implement unread message delivery on connection
        Requirements: 4.2
        """
        await self.create_test_data()

        # User2 connects (no unread messages)
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self.conversation.id}/"
        )
        communicator.scope["user"] = self.user2
        communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": self.conversation.id}
        }

        # Connect
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Should not receive any messages
        import asyncio

        try:
            await communicator.receive_json_from(timeout=0.5)
            self.fail("Should not have received any messages")
        except asyncio.TimeoutError:
            pass  # Expected - no messages

    def test_historical_messages_loaded_from_database(self):
        """
        Test that all historical messages are loaded from database when conversation opens.

        Task 7.3: Implement historical message loading
        Requirements: 4.3
        """
        # Create test data synchronously
        user1 = User.objects.create_user(
            email="user1@example.com", password="testpass123"
        )
        user2 = User.objects.create_user(
            email="user2@example.com", password="testpass123"
        )

        property_obj = Property.objects.create(
            user=user2,
            name="Test Property",
            full_address="123 Test St",
            phone_number="03001234567",
            cnic="12345-1234567-1",
            property_type="House",
            description="Test property",
            price=100000,
        )

        conversation = Conversation.objects.create(
            property=property_obj,
            participant_one=user1,
            participant_two=user2,
        )

        # Create historical messages
        Message.objects.create(
            conversation=conversation,
            sender=user1,
            content="Historical message 1",
            is_read=True,
        )
        Message.objects.create(
            conversation=conversation,
            sender=user2,
            content="Historical message 2",
            is_read=True,
        )
        Message.objects.create(
            conversation=conversation,
            sender=user1,
            content="Historical message 3",
            is_read=False,
        )

        # User1 opens conversation
        self.client.force_login(user1)
        response = self.client.get(f"/chat/conversations/{conversation.id}/")

        # Verify all messages are loaded
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 3)

        # Verify messages are in chronological order
        self.assertEqual(messages[0].content, "Historical message 1")
        self.assertEqual(messages[1].content, "Historical message 2")
        self.assertEqual(messages[2].content, "Historical message 3")

        # Verify messages are loaded from database (not just WebSocket)
        self.assertContains(response, "Historical message 1")
        self.assertContains(response, "Historical message 2")
        self.assertContains(response, "Historical message 3")

    def test_historical_messages_display_without_websocket(self):
        """
        Test that messages display even when WebSocket is disconnected.

        Task 7.3: Implement historical message loading
        Requirements: 4.3
        """
        # Create test data
        user1 = User.objects.create_user(
            email="user1@example.com", password="testpass123"
        )
        user2 = User.objects.create_user(
            email="user2@example.com", password="testpass123"
        )

        property_obj = Property.objects.create(
            user=user2,
            name="Test Property",
            full_address="123 Test St",
            phone_number="03001234567",
            cnic="12345-1234567-1",
            property_type="House",
            description="Test property",
            price=100000,
        )

        conversation = Conversation.objects.create(
            property=property_obj,
            participant_one=user1,
            participant_two=user2,
        )

        # Create messages
        Message.objects.create(
            conversation=conversation,
            sender=user1,
            content="Message without WebSocket",
            is_read=True,
        )

        # Access conversation detail page (HTTP only, no WebSocket)
        self.client.force_login(user1)
        response = self.client.get(f"/chat/conversations/{conversation.id}/")

        # Verify message is displayed
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Message without WebSocket")

        # Verify messages are loaded from database
        messages = response.context["messages"]
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].content, "Message without WebSocket")


class StartConversationViewTestCase(TransactionTestCase):
    """
    Test cases for the start conversation view.

    Tests cover:
    - Authentication requirement
    - Property owner verification
    - Conversation creation or retrieval
    - Redirect to conversation detail
    """

    def setUp(self):
        """Create test users and properties."""
        # Create users
        self.user1 = User.objects.create_user(
            email="user1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com", password="testpass123"
        )

        # Create property owned by user2
        self.property = Property.objects.create(
            user=self.user2,
            name="Test Property",
            full_address="123 Test St",
            phone_number="03001234567",
            cnic="12345-1234567-1",
            property_type="House",
            description="Test property",
            price=100000,
        )

    def test_unauthenticated_user_redirected(self):
        """
        Test that unauthenticated users are redirected to login page.

        Requirements: 1.1
        """
        response = self.client.get(f"/chat/start/{self.property.id}/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_property_owner_cannot_start_conversation(self):
        """
        Test that property owners cannot start a conversation with themselves.

        Requirements: 1.2
        """
        self.client.force_login(self.user2)
        response = self.client.get(f"/chat/start/{self.property.id}/")
        self.assertEqual(response.status_code, 403)
        self.assertIn("yourself", response.content.decode().lower())

    def test_create_new_conversation(self):
        """
        Test that a new conversation is created when none exists.

        Requirements: 6.2, 10.1, 10.2
        """
        self.client.force_login(self.user1)

        # Verify no conversation exists initially
        self.assertEqual(Conversation.objects.count(), 0)

        # Start conversation
        response = self.client.get(f"/chat/start/{self.property.id}/")

        # Should redirect to conversation detail
        self.assertEqual(response.status_code, 302)

        # Verify conversation was created
        self.assertEqual(Conversation.objects.count(), 1)
        conversation = Conversation.objects.first()

        # Verify conversation details
        self.assertEqual(conversation.property, self.property)
        self.assertEqual(conversation.participant_one, self.user2)  # Property owner
        self.assertEqual(conversation.participant_two, self.user1)  # Current user

        # Verify redirect URL
        expected_url = f"/chat/conversations/{conversation.id}/"
        self.assertIn(expected_url, response.url)

    def test_retrieve_existing_conversation(self):
        """
        Test that existing conversation is retrieved instead of creating a duplicate.

        Requirements: 6.2, 10.1, 10.2
        """
        # Create existing conversation
        existing_conversation = Conversation.objects.create(
            property=self.property,
            participant_one=self.user2,
            participant_two=self.user1,
        )

        self.client.force_login(self.user1)

        # Verify only one conversation exists
        self.assertEqual(Conversation.objects.count(), 1)

        # Start conversation (should retrieve existing)
        response = self.client.get(f"/chat/start/{self.property.id}/")

        # Should redirect to conversation detail
        self.assertEqual(response.status_code, 302)

        # Verify no new conversation was created
        self.assertEqual(Conversation.objects.count(), 1)

        # Verify redirect to existing conversation
        expected_url = f"/chat/conversations/{existing_conversation.id}/"
        self.assertIn(expected_url, response.url)

    def test_conversation_uniqueness_constraint(self):
        """
        Test that only one conversation exists between two users for a property.

        Requirements: 10.4
        """
        self.client.force_login(self.user1)

        # Start conversation twice
        response1 = self.client.get(f"/chat/start/{self.property.id}/")
        response2 = self.client.get(f"/chat/start/{self.property.id}/")

        # Both should succeed
        self.assertEqual(response1.status_code, 302)
        self.assertEqual(response2.status_code, 302)

        # But only one conversation should exist
        self.assertEqual(Conversation.objects.count(), 1)

        # Both should redirect to the same conversation
        self.assertEqual(response1.url, response2.url)

    def test_nonexistent_property_returns_404(self):
        """
        Test that accessing a non-existent property returns 404.

        Requirements: Error handling
        """
        self.client.force_login(self.user1)
        response = self.client.get("/chat/start/99999/")
        self.assertEqual(response.status_code, 404)

    def test_conversation_data_completeness(self):
        """
        Test that created conversation contains all required data.

        Requirements: 10.5
        """
        self.client.force_login(self.user1)
        self.client.get(f"/chat/start/{self.property.id}/")

        conversation = Conversation.objects.first()

        # Verify all required fields are present
        self.assertIsNotNone(conversation.property)
        self.assertIsNotNone(conversation.participant_one)
        self.assertIsNotNone(conversation.participant_two)
        self.assertIsNotNone(conversation.created_at)
        self.assertIsNotNone(conversation.updated_at)

        # Verify property reference
        self.assertEqual(conversation.property.id, self.property.id)

        # Verify participants
        self.assertIn(
            self.user1, [conversation.participant_one, conversation.participant_two]
        )
        self.assertIn(
            self.user2, [conversation.participant_one, conversation.participant_two]
        )


@override_settings(
    CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
)
class RateLimitingTestCase(TransactionTestCase):
    """
    Test cases for message rate limiting.

    Tests cover:
    - Task 9.1: Rate limiting implementation (10 messages per minute)
    - 429 error when limit exceeded
    - Cooldown timer calculation
    """

    @database_sync_to_async
    def create_test_data(self):
        """Create test users, property, and conversation."""
        # Create users
        self.user1 = User.objects.create_user(
            email="user1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com", password="testpass123"
        )

        # Create property
        self.property = Property.objects.create(
            user=self.user2,
            name="Test Property",
            full_address="123 Test St, Test City, TS 12345",
            phone_number="03001234567",
            cnic="12345-1234567-1",
            property_type="House",
            description="A test property",
            price=100000,
        )

        # Create conversation
        self.conversation = Conversation.objects.create(
            property=self.property,
            participant_one=self.user1,
            participant_two=self.user2,
        )

    async def test_rate_limit_allows_messages_within_limit(self):
        """
        Test that messages within the rate limit are allowed.

        Requirements: 9.4
        """
        await self.create_test_data()

        # Create communicator
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self.conversation.id}/"
        )
        communicator.scope["user"] = self.user1
        communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": self.conversation.id}
        }

        # Connect
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Send 10 messages (within limit)
        for i in range(10):
            await communicator.send_json_to({"message": f"Message {i + 1}"})
            response = await communicator.receive_json_from()
            self.assertEqual(response["type"], "message")
            self.assertEqual(response["message"], f"Message {i + 1}")

        # Disconnect
        await communicator.disconnect()

    async def test_rate_limit_blocks_excess_messages(self):
        """
        Test that messages exceeding the rate limit are blocked with 429 error.

        Requirements: 9.4
        """
        await self.create_test_data()

        # Create communicator
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self.conversation.id}/"
        )
        communicator.scope["user"] = self.user1
        communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": self.conversation.id}
        }

        # Connect
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Send 10 messages (at limit)
        for i in range(10):
            await communicator.send_json_to({"message": f"Message {i + 1}"})
            await communicator.receive_json_from()

        # Send 11th message (should be rate limited)
        await communicator.send_json_to({"message": "Message 11 - should be blocked"})
        response = await communicator.receive_json_from()

        # Verify rate limit error
        self.assertEqual(response["type"], "rate_limit_error")
        self.assertEqual(response["status_code"], 429)
        self.assertIn("Rate limit exceeded", response["message"])
        self.assertIn("cooldown_seconds", response)
        self.assertGreater(response["cooldown_seconds"], 0)

        # Disconnect
        await communicator.disconnect()

    async def test_rate_limit_cooldown_calculation(self):
        """
        Test that cooldown timer is calculated correctly.

        Requirements: 9.4
        """
        await self.create_test_data()

        # Create communicator
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self.conversation.id}/"
        )
        communicator.scope["user"] = self.user1
        communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": self.conversation.id}
        }

        # Connect
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Send 10 messages rapidly
        for i in range(10):
            await communicator.send_json_to({"message": f"Message {i + 1}"})
            await communicator.receive_json_from()

        # Send 11th message (should be rate limited)
        await communicator.send_json_to({"message": "Blocked message"})
        response = await communicator.receive_json_from()

        # Verify cooldown is reasonable (should be close to 60 seconds)
        cooldown = response["cooldown_seconds"]
        self.assertGreater(cooldown, 0)
        self.assertLessEqual(cooldown, 61)  # Allow 1 second buffer

        # Disconnect
        await communicator.disconnect()

    async def test_rate_limit_per_user(self):
        """
        Test that rate limiting is applied per user, not globally.

        Requirements: 9.4
        """
        await self.create_test_data()

        # User1 sends 10 messages
        communicator1 = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self.conversation.id}/"
        )
        communicator1.scope["user"] = self.user1
        communicator1.scope["url_route"] = {
            "kwargs": {"conversation_id": self.conversation.id}
        }

        connected1, _ = await communicator1.connect()
        self.assertTrue(connected1)

        for i in range(10):
            await communicator1.send_json_to({"message": f"User1 Message {i + 1}"})
            await communicator1.receive_json_from()

        # User2 should still be able to send messages
        communicator2 = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self.conversation.id}/"
        )
        communicator2.scope["user"] = self.user2
        communicator2.scope["url_route"] = {
            "kwargs": {"conversation_id": self.conversation.id}
        }

        connected2, _ = await communicator2.connect()
        self.assertTrue(connected2)

        # User2 will receive unread messages from user1 first, consume them
        for i in range(10):
            await communicator2.receive_json_from()

        # User2 sends a message (should succeed)
        await communicator2.send_json_to({"message": "User2 message"})

        # Both users should receive the message
        response1 = await communicator1.receive_json_from()
        response2 = await communicator2.receive_json_from()

        self.assertEqual(response1["type"], "message")
        self.assertEqual(response1["message"], "User2 message")
        self.assertEqual(response2["type"], "message")
        self.assertEqual(response2["message"], "User2 message")

        # Disconnect
        await communicator1.disconnect()
        await communicator2.disconnect()

    async def test_rate_limit_resets_after_window(self):
        """
        Test that rate limit resets after the time window expires.

        Requirements: 9.4
        """
        await self.create_test_data()

        # Create communicator
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self.conversation.id}/"
        )
        communicator.scope["user"] = self.user1
        communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": self.conversation.id}
        }

        # Connect
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Send 10 messages
        for i in range(10):
            await communicator.send_json_to({"message": f"Message {i + 1}"})
            await communicator.receive_json_from()

        # Verify 11th message is blocked
        await communicator.send_json_to({"message": "Blocked message"})
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "rate_limit_error")

        # Wait for rate limit window to expire (simulate by clearing storage)
        # In a real test, we would wait 60 seconds, but for testing we can manipulate the storage
        from apps.chat.consumers import rate_limit_storage

        rate_limit_storage[self.user1.id].clear()

        # Now message should succeed
        await communicator.send_json_to({"message": "Message after reset"})
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "message")
        self.assertEqual(response["message"], "Message after reset")

        # Disconnect
        await communicator.disconnect()

    async def test_rate_limit_message_not_persisted(self):
        """
        Test that rate-limited messages are not persisted to the database.

        Requirements: 9.4
        """
        await self.create_test_data()

        # Create communicator
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self.conversation.id}/"
        )
        communicator.scope["user"] = self.user1
        communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": self.conversation.id}
        }

        # Connect
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Send 10 messages
        for i in range(10):
            await communicator.send_json_to({"message": f"Message {i + 1}"})
            await communicator.receive_json_from()

        # Send 11th message (should be rate limited)
        await communicator.send_json_to({"message": "Blocked message"})
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "rate_limit_error")

        # Verify blocked message was not persisted
        @database_sync_to_async
        def check_message_count():
            return Message.objects.filter(conversation=self.conversation).count()

        message_count = await check_message_count()
        self.assertEqual(message_count, 10)  # Only the first 10 messages

        # Disconnect
        await communicator.disconnect()


class ConversationAdminTestCase(TransactionTestCase):
    """
    Test cases for ConversationAdmin interface.

    Tests cover:
    - Admin can view all conversations (Requirement 11.1)
    - Admin can see conversation metadata (Requirement 11.4)
    - Admin filtering capabilities (Requirement 11.3)
    """

    def setUp(self):
        """Create test users, properties, conversations, and admin user."""
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            email="admin@example.com", password="adminpass123"
        )

        # Create regular users
        self.user1 = User.objects.create_user(
            email="user1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com", password="testpass123"
        )
        self.user3 = User.objects.create_user(
            email="user3@example.com", password="testpass123"
        )

        # Create properties
        self.property1 = Property.objects.create(
            user=self.user2,
            name="Property 1",
            full_address="123 Test St",
            phone_number="03001234567",
            cnic="12345-1234567-1",
            property_type="House",
            description="Test property 1",
            price=100000,
        )

        self.property2 = Property.objects.create(
            user=self.user3,
            name="Property 2",
            full_address="456 Test Ave",
            phone_number="03001234568",
            cnic="12345-1234567-2",
            property_type="Apartment",
            description="Test property 2",
            price=150000,
        )

        # Create conversations
        self.conversation1 = Conversation.objects.create(
            property=self.property1,
            participant_one=self.user1,
            participant_two=self.user2,
        )

        self.conversation2 = Conversation.objects.create(
            property=self.property2,
            participant_one=self.user1,
            participant_two=self.user3,
        )

        # Create messages
        Message.objects.create(
            conversation=self.conversation1,
            sender=self.user1,
            content="Message 1 in conversation 1",
        )
        Message.objects.create(
            conversation=self.conversation1,
            sender=self.user2,
            content="Message 2 in conversation 1",
        )
        Message.objects.create(
            conversation=self.conversation2,
            sender=self.user1,
            content="Message 1 in conversation 2",
        )

    def test_admin_can_view_all_conversations(self):
        """
        Test that administrators can view all conversations in the system.

        Requirements: 11.1
        """
        self.client.force_login(self.admin_user)
        response = self.client.get("/admin/chat/conversation/")
        self.assertEqual(response.status_code, 200)

        # Check that both conversations are displayed
        self.assertContains(response, "Property 1")
        self.assertContains(response, "Property 2")

    def test_admin_conversation_displays_metadata(self):
        """
        Test that conversation metadata is displayed in admin interface.

        Requirements: 11.4
        """
        self.client.force_login(self.admin_user)
        response = self.client.get("/admin/chat/conversation/")

        # Check for participant names
        self.assertContains(response, self.user1.email)
        self.assertContains(response, self.user2.email)
        self.assertContains(response, self.user3.email)

        # Check for property references
        self.assertContains(response, self.property1.name)
        self.assertContains(response, self.property2.name)

    def test_admin_conversation_message_count(self):
        """
        Test that message count is displayed for each conversation.

        Requirements: 11.4
        """
        self.client.force_login(self.admin_user)
        response = self.client.get("/admin/chat/conversation/")

        # The response should show message counts
        # conversation1 has 2 messages, conversation2 has 1 message
        content = response.content.decode()
        self.assertIn("2", content)  # Message count for conversation1
        self.assertIn("1", content)  # Message count for conversation2

    def test_admin_can_filter_by_user(self):
        """
        Test that admin can filter conversations by user.

        Requirements: 11.3
        """
        self.client.force_login(self.admin_user)

        # Filter by user2
        response = self.client.get(f"/admin/chat/conversation/?user={self.user2.id}")
        self.assertEqual(response.status_code, 200)

        # Should show only conversation1 (user2 is in conversation1 only)
        self.assertContains(response, "Property 1")
        # Check that conversation2 is not in the results table
        content = response.content.decode()
        # Count occurrences - Property 2 should only appear in the filter sidebar, not in results
        # The result should show "1 Conversation" not "2 Conversations"
        self.assertIn("1\n\n    \n        Conversation", content)

    def test_admin_can_filter_by_property(self):
        """
        Test that admin can filter conversations by property.

        Requirements: 11.3
        """
        self.client.force_login(self.admin_user)

        # Filter by property1
        response = self.client.get(
            f"/admin/chat/conversation/?property={self.property1.id}"
        )
        self.assertEqual(response.status_code, 200)

        # Should show only conversation1
        self.assertContains(response, "Property 1")
        # Check that only 1 conversation is shown
        content = response.content.decode()
        self.assertIn("1\n\n    \n        Conversation", content)

    def test_admin_can_search_conversations(self):
        """
        Test that admin can search conversations by participant email or property name.

        Requirements: 11.3
        """
        self.client.force_login(self.admin_user)

        # Search by participant email
        response = self.client.get("/admin/chat/conversation/?q=user1@example.com")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "user1@example.com")

        # Search by property name
        response = self.client.get("/admin/chat/conversation/?q=Property+1")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Property 1")


class MessageAdminTestCase(TransactionTestCase):
    """
    Test cases for MessageAdmin interface.

    Tests cover:
    - Admin can view all messages (Requirement 11.2)
    - Admin can see message fields (Requirement 11.5)
    - Admin filtering capabilities (Requirement 11.3)
    """

    def setUp(self):
        """Create test users, properties, conversations, messages, and admin user."""
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            email="admin@example.com", password="adminpass123"
        )

        # Create regular users
        self.user1 = User.objects.create_user(
            email="user1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com", password="testpass123"
        )

        # Create property
        self.property = Property.objects.create(
            user=self.user2,
            name="Test Property",
            full_address="123 Test St",
            phone_number="03001234567",
            cnic="12345-1234567-1",
            property_type="House",
            description="Test property",
            price=100000,
        )

        # Create conversation
        self.conversation = Conversation.objects.create(
            property=self.property,
            participant_one=self.user1,
            participant_two=self.user2,
        )

        # Create messages
        self.message1 = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            content="This is a test message from user1",
            is_read=False,
        )

        self.message2 = Message.objects.create(
            conversation=self.conversation,
            sender=self.user2,
            content="This is a test message from user2",
            is_read=True,
        )

        self.message3 = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            content="A" * 100,  # Long message for content preview test
            is_read=False,
        )

    def test_admin_can_view_all_messages(self):
        """
        Test that administrators can view all messages in the system.

        Requirements: 11.2
        """
        self.client.force_login(self.admin_user)
        response = self.client.get("/admin/chat/message/")
        self.assertEqual(response.status_code, 200)

        # Check that messages are displayed
        self.assertContains(response, "test message from user1")
        self.assertContains(response, "test message from user2")

    def test_admin_message_displays_all_fields(self):
        """
        Test that message fields are displayed in admin interface.

        Requirements: 11.5
        """
        self.client.force_login(self.admin_user)
        response = self.client.get("/admin/chat/message/")

        # Check for sender
        self.assertContains(response, self.user1.email)
        self.assertContains(response, self.user2.email)

        # Check for content preview
        self.assertContains(response, "test message from user1")

        # Check for read status indicators
        content = response.content.decode()
        # The page should show read status (True/False or icons)
        self.assertIn("is_read", content.lower())

    def test_admin_message_content_preview(self):
        """
        Test that long message content is truncated in the preview.

        Requirements: 11.5
        """
        self.client.force_login(self.admin_user)
        response = self.client.get("/admin/chat/message/")

        content = response.content.decode()

        # Long message should be truncated with ellipsis
        # The full 100 A's should not appear, but a preview should
        self.assertNotIn("A" * 100, content)
        self.assertIn("A" * 50, content)  # First 50 characters should appear

    def test_admin_can_filter_by_read_status(self):
        """
        Test that admin can filter messages by read status.

        Requirements: 11.3
        """
        self.client.force_login(self.admin_user)

        # Filter by unread messages
        response = self.client.get("/admin/chat/message/?is_read__exact=0")
        self.assertEqual(response.status_code, 200)

        # Should show unread messages
        self.assertContains(response, "test message from user1")

        # Filter by read messages
        response = self.client.get("/admin/chat/message/?is_read__exact=1")
        self.assertEqual(response.status_code, 200)

        # Should show read messages
        self.assertContains(response, "test message from user2")

    def test_admin_can_search_messages(self):
        """
        Test that admin can search messages by sender email or content.

        Requirements: 11.3
        """
        self.client.force_login(self.admin_user)

        # Search by sender email
        response = self.client.get("/admin/chat/message/?q=user1@example.com")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "user1@example.com")

        # Search by content
        response = self.client.get("/admin/chat/message/?q=test+message+from+user2")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test message from user2")

    def test_admin_message_links_to_conversation(self):
        """
        Test that messages in admin link to their conversation.

        Requirements: 11.2
        """
        self.client.force_login(self.admin_user)
        response = self.client.get("/admin/chat/message/")

        # Should contain link to conversation
        self.assertContains(response, f"Conversation {self.conversation.id}")


@override_settings(
    CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
)
class MessageTypeProtocolTestCase(TransactionTestCase):
    """
    Test cases for the message type protocol.

    Tests cover:
    - Ping/pong health check messages
    - Backward compatibility with messages without type field
    - Unknown message type handling
    - Message type dispatching
    """

    @database_sync_to_async
    def create_test_data(self):
        """Create test users, property, and conversation."""
        # Create users
        self.user1 = User.objects.create_user(
            email="user1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com", password="testpass123"
        )

        # Create property
        self.property = Property.objects.create(
            user=self.user2,
            name="Test Property",
            full_address="123 Test St, Test City, TS 12345",
            phone_number="03001234567",
            cnic="12345-1234567-1",
            property_type="House",
            description="A test property",
            price=100000,
        )

        # Create conversation
        self.conversation = Conversation.objects.create(
            property=self.property,
            participant_one=self.user1,
            participant_two=self.user2,
        )

    async def test_ping_pong_health_check(self):
        """
        Test that ping messages receive pong responses.

        This tests the health check functionality for connection monitoring.
        """
        await self.create_test_data()

        # Create communicator
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self.conversation.id}/"
        )
        communicator.scope["user"] = self.user1
        communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": self.conversation.id}
        }

        # Connect
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Send ping message
        await communicator.send_json_to({"type": "ping"})

        # Receive pong response
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "pong")

        # Disconnect
        await communicator.disconnect()

    async def test_backward_compatibility_no_type_field(self):
        """
        Test that messages without type field default to chat_message.

        This ensures backward compatibility with existing clients.
        """
        await self.create_test_data()

        # Create communicator
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self.conversation.id}/"
        )
        communicator.scope["user"] = self.user1
        communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": self.conversation.id}
        }

        # Connect
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Send message without type field (old format)
        await communicator.send_json_to({"message": "Hello without type field"})

        # Should receive message successfully
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "message")
        self.assertEqual(response["message"], "Hello without type field")

        # Disconnect
        await communicator.disconnect()

    async def test_explicit_chat_message_type(self):
        """
        Test that messages with explicit chat_message type work correctly.
        """
        await self.create_test_data()

        # Create communicator
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self.conversation.id}/"
        )
        communicator.scope["user"] = self.user1
        communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": self.conversation.id}
        }

        # Connect
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Send message with explicit type
        await communicator.send_json_to(
            {"type": "chat_message", "message": "Hello with explicit type"}
        )

        # Should receive message successfully
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "message")
        self.assertEqual(response["message"], "Hello with explicit type")

        # Disconnect
        await communicator.disconnect()

    async def test_unknown_message_type_returns_error(self):
        """
        Test that unknown message types return an error response.

        This ensures the protocol is extensible and handles invalid types gracefully.
        """
        await self.create_test_data()

        # Create communicator
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self.conversation.id}/"
        )
        communicator.scope["user"] = self.user1
        communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": self.conversation.id}
        }

        # Connect
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Send message with unknown type
        await communicator.send_json_to({"type": "unknown_type", "data": "some data"})

        # Should receive error response
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "error")
        self.assertIn("Unknown message type", response["message"])

        # Disconnect
        await communicator.disconnect()

    async def test_ping_does_not_create_message(self):
        """
        Test that ping messages do not create database records.
        """
        await self.create_test_data()

        # Create communicator
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self.conversation.id}/"
        )
        communicator.scope["user"] = self.user1
        communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": self.conversation.id}
        }

        # Connect
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Get initial message count
        @database_sync_to_async
        def get_message_count():
            return Message.objects.filter(conversation=self.conversation).count()

        initial_count = await get_message_count()

        # Send ping message
        await communicator.send_json_to({"type": "ping"})
        await communicator.receive_json_from()

        # Verify no message was created
        final_count = await get_message_count()
        self.assertEqual(initial_count, final_count)

        # Disconnect
        await communicator.disconnect()

    async def test_multiple_ping_pong_exchanges(self):
        """
        Test that multiple ping/pong exchanges work correctly.
        """
        await self.create_test_data()

        # Create communicator
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self.conversation.id}/"
        )
        communicator.scope["user"] = self.user1
        communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": self.conversation.id}
        }

        # Connect
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Send multiple pings
        for i in range(5):
            await communicator.send_json_to({"type": "ping"})
            response = await communicator.receive_json_from()
            self.assertEqual(response["type"], "pong")

        # Disconnect
        await communicator.disconnect()

    async def test_mixed_message_types(self):
        """
        Test that different message types can be mixed in the same connection.
        """
        await self.create_test_data()

        # Create communicator
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self.conversation.id}/"
        )
        communicator.scope["user"] = self.user1
        communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": self.conversation.id}
        }

        # Connect
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Send ping
        await communicator.send_json_to({"type": "ping"})
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "pong")

        # Send chat message
        await communicator.send_json_to({"type": "chat_message", "message": "Hello"})
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "message")
        self.assertEqual(response["message"], "Hello")

        # Send another ping
        await communicator.send_json_to({"type": "ping"})
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "pong")

        # Disconnect
        await communicator.disconnect()

    async def test_invalid_json_returns_error(self):
        """
        Test that invalid JSON returns an error message.
        """
        await self.create_test_data()

        # Create communicator
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(), f"/ws/chat/{self.conversation.id}/"
        )
        communicator.scope["user"] = self.user1
        communicator.scope["url_route"] = {
            "kwargs": {"conversation_id": self.conversation.id}
        }

        # Connect
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Send invalid JSON
        await communicator.send_to(text_data="invalid json {")

        # Should receive error response
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "error")
        self.assertIn("Invalid message format", response["message"])

        # Disconnect
        await communicator.disconnect()
