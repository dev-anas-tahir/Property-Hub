from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from apps.chat.models import Conversation


@login_required
def conversation_list(request):
    """
    Display all conversations for authenticated user.

    Requirements:
    - 5.1: Query conversations where user is participant
    - 5.4: Order by updated_at descending
    - 5.5: Annotate with unread message count
    """
    user = request.user

    # Query conversations where user is either participant_one or participant_two
    conversations = (
        Conversation.objects.filter(Q(participant_one=user) | Q(participant_two=user))
        .select_related("property", "participant_one", "participant_two")
        .prefetch_related("messages")
        .order_by("-updated_at")
    )

    # Add helper attributes for each conversation
    for conversation in conversations:
        # Identify the other participant
        if conversation.participant_one == user:
            conversation.other_participant = conversation.participant_two
        else:
            conversation.other_participant = conversation.participant_one

        # Count unread messages where the user is NOT the sender
        conversation.unread_count = (
            conversation.messages.filter(is_read=False).exclude(sender=user).count()
        )

    context = {
        "conversations": conversations,
    }

    return render(request, "chat/conversation_list.html", context)


@login_required
def conversation_detail(request, conversation_id):
    """
    Display single conversation with message history.

    Requirements:
    - 3.2: Load all messages ordered chronologically
    - 7.2: Mark messages as read for current user
    - 7.3: Mark messages as read when conversation opened
    """
    from django.shortcuts import get_object_or_404
    from django.http import HttpResponseForbidden

    user = request.user

    # Get conversation and verify user is a participant
    conversation = get_object_or_404(Conversation, id=conversation_id)

    # Verify user is participant (authorization check)
    if conversation.participant_one != user and conversation.participant_two != user:
        return HttpResponseForbidden("You are not a participant in this conversation.")

    # Load all messages ordered chronologically (by created_at)
    messages = conversation.messages.select_related("sender").order_by("created_at")

    # Mark messages as read for current user
    # Only mark messages where the current user is the recipient (not the sender)
    conversation.messages.filter(is_read=False).exclude(sender=user).update(
        is_read=True
    )

    # Identify the other participant
    if conversation.participant_one == user:
        other_participant = conversation.participant_two
    else:
        other_participant = conversation.participant_one

    context = {
        "conversation": conversation,
        "chat_messages": messages,
        "other_participant": other_participant,
    }

    return render(request, "chat/conversation_detail.html", context)


@login_required
def start_conversation(request, property_id):
    """
    Create or retrieve conversation for a property.

    Requirements:
    - 1.1: Verify user is authenticated (handled by @login_required)
    - 1.2: Verify user is not property owner
    - 6.2: Get or create conversation
    - 10.1: Check if conversation already exists
    - 10.2: Create new conversation if it doesn't exist
    """
    from django.shortcuts import get_object_or_404, redirect
    from django.http import HttpResponseForbidden
    from apps.properties.models import Property

    user = request.user

    # Get the property
    property_obj = get_object_or_404(Property, id=property_id)

    # Verify user is not the property owner
    if property_obj.user == user:
        return HttpResponseForbidden(
            "You cannot start a conversation with yourself about your own property."
        )

    # Get or create conversation
    # Ensure consistent ordering of participants to avoid duplicates
    # Always put the property owner as participant_one
    conversation, created = Conversation.objects.get_or_create(
        property=property_obj, participant_one=property_obj.user, participant_two=user
    )

    # Redirect to conversation detail
    return redirect("chat:conversation_detail", conversation_id=conversation.id)
