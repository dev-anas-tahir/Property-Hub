import time

from django.db.models import Q, QuerySet

from apps.chat.models import Conversation


def conversation_list_for_user(*, user) -> QuerySet:
    return (
        Conversation.objects.filter(Q(participant_one=user) | Q(participant_two=user))
        .select_related("property", "participant_one", "participant_two")
        .prefetch_related("messages")
        .order_by("-updated_at")
    )


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
