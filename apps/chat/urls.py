"""
URL configuration for the chat app.
"""

from django.urls import path

from apps.chat.views import (
    ConversationDetailView,
    ConversationListView,
    StartConversationView,
)

app_name = "chat"

urlpatterns = [
    path("conversations/", ConversationListView.as_view(), name="conversation_list"),
    path(
        "conversations/<int:conversation_id>/",
        ConversationDetailView.as_view(),
        name="conversation_detail",
    ),
    path(
        "start/<int:property_id>/",
        StartConversationView.as_view(),
        name="start_conversation",
    ),
]
