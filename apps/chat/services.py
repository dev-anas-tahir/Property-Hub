import time
from dataclasses import dataclass
from enum import Enum

import nh3
from channels.db import database_sync_to_async

from apps.chat.models import Conversation, Message
from apps.shared.exceptions import ApplicationError

RATE_LIMIT_MESSAGES = 10
RATE_LIMIT_WINDOW = 60


class MessageDeliveryStatus(Enum):
    DELIVERED = "delivered"
    REJECTED = "rejected"
    RATE_LIMITED = "rate_limited"


@dataclass(frozen=True)
class MessageDeliveryResult:
    status: MessageDeliveryStatus
    message: Message | None = None
    payload: dict | None = None
    error_message: str = ""
    cooldown_seconds: int = 0


def message_create(*, conversation: Conversation, sender, content: str) -> Message:
    message = Message(conversation=conversation, sender=sender, content=content)
    message.full_clean()
    message.save()
    conversation.save(update_fields=["updated_at"])
    return message


async def message_deliver(
    *, conversation: Conversation, sender, content: str, redis_url: str
) -> MessageDeliveryResult:
    content = content.strip() if isinstance(content, str) else ""
    if not content:
        return MessageDeliveryResult(
            status=MessageDeliveryStatus.REJECTED,
            error_message="Message content cannot be empty",
        )

    if len(content) > 5000:
        return MessageDeliveryResult(
            status=MessageDeliveryStatus.REJECTED,
            error_message="Message exceeds maximum length of 5000 characters",
        )

    is_allowed, cooldown_seconds = await rate_limit_check(
        user_id=sender.id, redis_url=redis_url
    )
    if not is_allowed:
        return MessageDeliveryResult(
            status=MessageDeliveryStatus.RATE_LIMITED,
            error_message=(
                "Rate limit exceeded. Please wait "
                f"{cooldown_seconds} seconds before sending another message."
            ),
            cooldown_seconds=cooldown_seconds,
        )

    recipient_id = (
        conversation.participant_two_id
        if conversation.participant_one_id == sender.id
        else conversation.participant_one_id
    )
    if recipient_id == sender.id:
        return MessageDeliveryResult(
            status=MessageDeliveryStatus.REJECTED,
            error_message="Cannot send messages to yourself",
        )

    sanitized_content = nh3.clean(content, tags=set())
    message = await database_sync_to_async(message_create)(
        conversation=conversation,
        sender=sender,
        content=sanitized_content,
    )
    return MessageDeliveryResult(
        status=MessageDeliveryStatus.DELIVERED,
        message=message,
        payload={
            "message": sanitized_content,
            "sender_id": sender.id,
            "sender_email": sender.email,
            "message_id": message.id,
            "created_at": message.created_at.isoformat(),
        },
    )


def conversation_get_or_create(
    *, property_obj, participant_one, participant_two
) -> tuple[Conversation, bool]:
    return Conversation.objects.get_or_create(
        property=property_obj,
        participant_one=participant_one,
        participant_two=participant_two,
    )


def messages_mark_read(*, conversation: Conversation, user) -> None:
    conversation.messages.filter(is_read=False).exclude(sender=user).update(
        is_read=True
    )


async def rate_limit_check(*, user_id: int, redis_url: str) -> tuple[bool, int]:
    from redis.asyncio import Redis as AsyncRedis

    from apps.chat.selectors import rate_limit_get_cooldown

    current_time = time.time()
    key = f"rate_limit:chat:{user_id}"
    window_start = current_time - RATE_LIMIT_WINDOW

    async with AsyncRedis.from_url(redis_url, decode_responses=True) as redis:
        async with redis.pipeline(transaction=True) as pipe:
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zadd(key, {str(current_time): current_time})
            pipe.zcard(key)
            pipe.expire(key, RATE_LIMIT_WINDOW)
            _, _, message_count, _ = await pipe.execute()

    if message_count <= RATE_LIMIT_MESSAGES:
        return True, 0

    cooldown = await rate_limit_get_cooldown(
        user_id=user_id, redis_url=redis_url, rate_limit_window=RATE_LIMIT_WINDOW
    )
    return False, cooldown


def conversation_start(*, user, property_obj) -> Conversation:
    if property_obj.user == user:
        raise ApplicationError(
            "You cannot start a conversation with yourself about your own property."
        )
    conversation, _ = conversation_get_or_create(
        property_obj=property_obj,
        participant_one=property_obj.user,
        participant_two=user,
    )
    return conversation
