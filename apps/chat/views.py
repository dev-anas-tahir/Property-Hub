from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from apps.chat.models import Conversation
from apps.chat.selectors import conversation_list_for_user, messages_for_conversation
from apps.chat.services import conversation_start, messages_mark_read
from apps.properties.models import Property
from apps.shared.exceptions import ApplicationError


class ConversationListView(LoginRequiredMixin, View):
    def get(self, request):
        conversations = conversation_list_for_user(user=request.user)

        for conversation in conversations:
            if conversation.participant_one == request.user:
                conversation.other_participant = conversation.participant_two
            else:
                conversation.other_participant = conversation.participant_one

            conversation.unread_count = (
                conversation.messages.filter(is_read=False)
                .exclude(sender=request.user)
                .count()
            )

        return render(
            request, "chat/conversation_list.html", {"conversations": conversations}
        )


class ConversationDetailView(LoginRequiredMixin, View):
    def get(self, request, conversation_id):
        conversation = get_object_or_404(Conversation, id=conversation_id)

        if (
            conversation.participant_one != request.user
            and conversation.participant_two != request.user
        ):
            return HttpResponseForbidden(
                "You are not a participant in this conversation."
            )

        chat_messages = messages_for_conversation(conversation=conversation)
        messages_mark_read(conversation=conversation, user=request.user)

        other_participant = (
            conversation.participant_two
            if conversation.participant_one == request.user
            else conversation.participant_one
        )

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
