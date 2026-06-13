"""Message service — send, receive, conversation queries.

AI-generated: business logic for private messaging.
"""

from __future__ import annotations

from app.core.errors import NotFoundError, ValidationError
from app.repositories.message_repository import Message, MessageRepository
from app.repositories.user_repository import InMemoryUserRepository
from app.schemas.message import (
    ConversationPreview,
    MessageView,
    SendMessageRequest,
    UnreadCountView,
)


class MessageService:
    def __init__(
        self,
        message_repository: MessageRepository,
        user_repository: InMemoryUserRepository,
    ) -> None:
        self.msg_repo = message_repository
        self.user_repo = user_repository

    def send(self, from_id: str, req: SendMessageRequest) -> MessageView:
        if from_id == req.to_user_id:
            raise ValidationError("cannot send message to yourself")
        self.user_repo.get(from_id)
        self.user_repo.get(req.to_user_id)

        msg = Message(
            from_id=from_id,
            to_id=req.to_user_id,
            content=req.content,
            image_url=req.image_url,
            is_read=False,
        )
        saved = self.msg_repo.create(msg)
        return self._to_view(saved)

    def get_conversation(self, user_id: str, partner_id: str, limit: int = 50) -> list[MessageView]:
        self.user_repo.get(user_id)
        self.user_repo.get(partner_id)
        self.msg_repo.mark_read(user_id, partner_id)
        msgs = self.msg_repo.list_conversation(user_id, partner_id, limit=limit)
        return [self._to_view(m) for m in msgs]

    def list_conversations(self, user_id: str) -> list[ConversationPreview]:
        self.user_repo.get(user_id)
        convos = self.msg_repo.list_conversations(user_id)
        results = []
        for c in convos:
            try:
                partner = self.user_repo.get(c["partner_id"])
                nickname = partner.profile.nickname
            except NotFoundError:
                nickname = "unknown"
            results.append(ConversationPreview(
                partner_id=c["partner_id"],
                partner_nickname=nickname,
                unread_count=c["unread_count"],
                last_message=c["last_message"],
                last_time=c["last_time"],
                last_from_me=c["last_from_me"],
            ))
        return results

    def get_unread_count(self, user_id: str) -> UnreadCountView:
        count = self.msg_repo.unread_count(user_id)
        return UnreadCountView(unread_count=count)

    def _to_view(self, msg: Message) -> MessageView:
        try:
            from_user = self.user_repo.get(msg.from_id)
            nick = from_user.profile.nickname
        except NotFoundError:
            nick = "unknown"
        return MessageView(
            id=msg.id,
            from_id=msg.from_id,
            from_nickname=nick,
            to_id=msg.to_id,
            content=msg.content,
            image_url=msg.image_url,
            created_at=msg.created_at,
            is_read=msg.is_read,
        )
