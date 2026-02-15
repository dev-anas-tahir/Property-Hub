"""
Admin interface for the real-time chat feature.

Provides administrative access to conversations and messages with filtering,
searching, and display capabilities as specified in Requirements 11.1-11.5.
"""

from django.contrib import admin
from django.db.models import Count, Q
from django.utils.html import format_html
from .models import Conversation, Message


class UserFilter(admin.SimpleListFilter):
    """Custom filter to find conversations by any participant."""

    title = "user"
    parameter_name = "user"

    def lookups(self, request, model_admin):
        # Get all users who are participants in conversations
        from django.contrib.auth import get_user_model

        User = get_user_model()
        users = (
            User.objects.filter(
                Q(conversations_as_p1__isnull=False)
                | Q(conversations_as_p2__isnull=False)
            )
            .distinct()
            .order_by("email")
        )
        return [(user.id, user.email) for user in users]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                Q(participant_one_id=self.value()) | Q(participant_two_id=self.value())
            )
        return queryset


class PropertyFilter(admin.SimpleListFilter):
    """Custom filter to find conversations by property."""

    title = "property"
    parameter_name = "property"

    def lookups(self, request, model_admin):
        # Get all properties that have conversations
        from apps.properties.models import Property

        properties = (
            Property.objects.filter(conversations__isnull=False)
            .distinct()
            .order_by("name")
        )
        return [(prop.id, prop.name) for prop in properties]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(property_id=self.value())
        return queryset


class DateRangeFilter(admin.SimpleListFilter):
    """Custom filter for date ranges."""

    title = "date range"
    parameter_name = "date_range"

    def lookups(self, request, model_admin):
        return [
            ("today", "Today"),
            ("week", "Past 7 days"),
            ("month", "Past 30 days"),
            ("year", "Past year"),
        ]

    def queryset(self, request, queryset):
        from django.utils import timezone
        from datetime import timedelta

        if self.value() == "today":
            date_from = timezone.now().date()
            return queryset.filter(created_at__date=date_from)
        elif self.value() == "week":
            date_from = timezone.now() - timedelta(days=7)
            return queryset.filter(created_at__gte=date_from)
        elif self.value() == "month":
            date_from = timezone.now() - timedelta(days=30)
            return queryset.filter(created_at__gte=date_from)
        elif self.value() == "year":
            date_from = timezone.now() - timedelta(days=365)
            return queryset.filter(created_at__gte=date_from)
        return queryset


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """
    Admin interface for viewing conversations.

    Validates Requirements 11.1, 11.3, 11.4:
    - Displays all conversations in the system
    - Provides filtering by user, property, and date range
    - Shows participant names, property reference, and message count
    """

    list_display = [
        "id",
        "property_link",
        "participant_one_link",
        "participant_two_link",
        "message_count",
        "created_at",
        "updated_at",
    ]

    list_filter = [
        UserFilter,
        PropertyFilter,
        DateRangeFilter,
        "created_at",
        "updated_at",
    ]

    search_fields = [
        "participant_one__email",
        "participant_two__email",
        "property__name",
    ]

    readonly_fields = ["created_at", "updated_at"]

    date_hierarchy = "created_at"

    def get_queryset(self, request):
        """Optimize queries by prefetching related objects."""
        queryset = super().get_queryset(request)
        return queryset.select_related(
            "property", "participant_one", "participant_two"
        ).annotate(msg_count=Count("messages"))

    def message_count(self, obj):
        """Display the number of messages in the conversation."""
        return obj.msg_count if hasattr(obj, "msg_count") else obj.messages.count()

    message_count.short_description = "Messages"
    message_count.admin_order_field = "msg_count"

    def property_link(self, obj):
        """Display property as a clickable link."""
        if obj.property:
            return format_html(
                '<a href="/admin/properties/property/{}/change/">{}</a>',
                obj.property.id,
                obj.property.name,
            )
        return "-"

    property_link.short_description = "Property"

    def participant_one_link(self, obj):
        """Display participant one as a clickable link."""
        if obj.participant_one:
            from django.contrib.auth import get_user_model

            User = get_user_model()
            model_name = User._meta.model_name
            app_label = User._meta.app_label
            return format_html(
                '<a href="/admin/{}/{}/{}/change/">{}</a>',
                app_label,
                model_name,
                obj.participant_one.id,
                obj.participant_one.email,
            )
        return "-"

    participant_one_link.short_description = "Participant 1"

    def participant_two_link(self, obj):
        """Display participant two as a clickable link."""
        if obj.participant_two:
            from django.contrib.auth import get_user_model

            User = get_user_model()
            model_name = User._meta.model_name
            app_label = User._meta.app_label
            return format_html(
                '<a href="/admin/{}/{}/{}/change/">{}</a>',
                app_label,
                model_name,
                obj.participant_two.id,
                obj.participant_two.email,
            )
        return "-"

    participant_two_link.short_description = "Participant 2"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Admin interface for viewing messages.

    Validates Requirements 11.2, 11.5:
    - Displays all messages in conversations
    - Shows sender, recipient, content, timestamp, and read status
    """

    list_display = [
        "id",
        "conversation_link",
        "sender_link",
        "content_preview",
        "created_at",
        "is_read",
    ]

    list_filter = [
        "is_read",
        "created_at",
        DateRangeFilter,
    ]

    search_fields = [
        "sender__email",
        "content",
        "conversation__participant_one__email",
        "conversation__participant_two__email",
    ]

    readonly_fields = ["created_at", "conversation", "sender"]

    date_hierarchy = "created_at"

    def get_queryset(self, request):
        """Optimize queries by prefetching related objects."""
        queryset = super().get_queryset(request)
        return queryset.select_related(
            "conversation",
            "sender",
            "conversation__participant_one",
            "conversation__participant_two",
        )

    def content_preview(self, obj):
        """Display a preview of the message content."""
        max_length = 50
        if len(obj.content) > max_length:
            return obj.content[:max_length] + "..."
        return obj.content

    content_preview.short_description = "Content"

    def conversation_link(self, obj):
        """Display conversation as a clickable link."""
        if obj.conversation:
            return format_html(
                '<a href="/admin/chat/conversation/{}/change/">Conversation {}</a>',
                obj.conversation.id,
                obj.conversation.id,
            )
        return "-"

    conversation_link.short_description = "Conversation"

    def sender_link(self, obj):
        """Display sender as a clickable link."""
        if obj.sender:
            from django.contrib.auth import get_user_model

            User = get_user_model()
            model_name = User._meta.model_name
            app_label = User._meta.app_label
            return format_html(
                '<a href="/admin/{}/{}/{}/change/">{}</a>',
                app_label,
                model_name,
                obj.sender.id,
                obj.sender.email,
            )
        return "-"

    sender_link.short_description = "Sender"
