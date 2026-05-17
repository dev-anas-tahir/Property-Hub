import time

from django.db.models import Count, Q, QuerySet
from django.shortcuts import get_object_or_404

from apps.chat.models import Conversation
from apps.shared.exceptions import ApplicationError


def conversation_list_for_user(*, user) -> list[Conversation]:
    conversations = list(
        Conversation.objects.filter(Q(participant_one=user) | Q(participant_two=user))
        .select_related("property", "participant_one", "participant_two")
        .annotate(
            unread_count=Count(
                "messages",
                filter=Q(messages__is_read=False) & ~Q(messages__sender=user),
            )
        )
        .order_by("-updated_at")
    )
    for conversation in conversations:
        conversation.other_participant = (
            conversation.participant_two
            if conversation.participant_one == user
            else conversation.participant_one
        )
    return conversations


def conversation_get_for_user(
    *, conversation_id: int, user
) -> tuple[Conversation, object]:
    conversation = get_object_or_404(
        Conversation.objects.select_related(
            "participant_one", "participant_two", "property"
        ),
        id=conversation_id,
    )
    if conversation.participant_one != user and conversation.participant_two != user:
        raise ApplicationError("You are not a participant in this conversation.")
    other_participant = (
        conversation.participant_two
        if conversation.participant_one == user
        else conversation.participant_one
    )
    return conversation, other_participant


def conversation_get(*, conversation_id: int) -> Conversation | None:
    return (
        Conversation.objects.filter(id=conversation_id)
        .select_related("participant_one", "participant_two", "property")
        .first()
    )


def messages_for_conversation(*, conversation: Conversation) -> QuerySet:
    return conversation.messages.select_related("sender").order_by("created_at")


async def rate_limit_get_cooldown(
    *, user_id: int, redis_url: str, rate_limit_window: int
) -> int:
    from redis.asyncio import Redis as AsyncRedis

    key = f"rate_limit:chat:{user_id}"
    async with AsyncRedis.from_url(redis_url, decode_responses=True) as redis:
        oldest = await redis.zrange(key, 0, 0, withscores=True)

    if oldest:
        oldest_timestamp = oldest[0][1]
        return int(oldest_timestamp + rate_limit_window - time.time()) + 1
    return rate_limit_window
