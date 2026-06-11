from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from apps.chat.selectors import (
    conversation_get_for_user,
    conversation_list_for_user,
    messages_for_conversation,
)
from apps.chat.services import conversation_start, messages_mark_read
from apps.properties.models import Property
from apps.shared.exceptions import ApplicationError


class ConversationListView(LoginRequiredMixin, View):
    def get(self, request):
        conversations = conversation_list_for_user(user=request.user)
        return render(
            request, "chat/conversation_list.html", {"conversations": conversations}
        )


class ConversationDetailView(LoginRequiredMixin, View):
    def get(self, request, conversation_id):
        try:
            conversation, other_participant = conversation_get_for_user(
                conversation_id=conversation_id, user=request.user
            )
        except ApplicationError as e:
            return HttpResponseForbidden(e.message)

        chat_messages = list(messages_for_conversation(conversation=conversation))
        for message in chat_messages:
            message.was_unread = not message.is_read and message.sender != request.user
        messages_mark_read(conversation=conversation, user=request.user)

        context = {
            "conversation": conversation,
            "chat_messages": chat_messages,
            "other_participant": other_participant,
        }
        return render(request, "chat/conversation_detail.html", context)


class StartConversationView(LoginRequiredMixin, View):
    def get(self, request, property_id):
        property_obj = get_object_or_404(Property, id=property_id)

        try:
            conversation = conversation_start(
                user=request.user, property_obj=property_obj
            )
        except ApplicationError as e:
            return HttpResponseForbidden(e.message)

        return redirect("chat:conversation_detail", conversation_id=conversation.id)
