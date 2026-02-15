"""
URL configuration for the chat app.
"""

from django.urls import path
from apps.chat import views

app_name = "chat"

urlpatterns = [
    path("conversations/", views.conversation_list, name="conversation_list"),
    path(
        "conversations/<int:conversation_id>/",
        views.conversation_detail,
        name="conversation_detail",
    ),
    path(
        "start/<int:property_id>/", views.start_conversation, name="start_conversation"
    ),
]
