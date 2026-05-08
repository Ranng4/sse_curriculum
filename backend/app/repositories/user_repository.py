from __future__ import annotations

from copy import deepcopy
from dataclasses import replace

from app.core.errors import ConflictError, NotFoundError
from app.models.user import User


class InMemoryUserRepository:
    def __init__(self) -> None:
        self._users: dict[str, User] = {}
        self._phone_index: dict[str, str] = {}
        self._email_index: dict[str, str] = {}
        self._wechat_index: dict[str, str] = {}
        self._weibo_index: dict[str, str] = {}

    def create(self, user: User) -> User:
        self._check_index_conflict(user)
        self._users[user.id] = deepcopy(user)
        self._refresh_indexes(user)
        return deepcopy(user)

    def save(self, user: User) -> User:
        if user.id not in self._users:
            raise NotFoundError("user not found")
        self._check_index_conflict(user)
        self._users[user.id] = deepcopy(user)
        self._refresh_indexes(user)
        return deepcopy(user)

    def get(self, user_id: str) -> User:
        user = self._users.get(user_id)
        if user is None:
            raise NotFoundError("user not found")
        return deepcopy(user)

    def find_by_phone(self, phone: str) -> User | None:
        user_id = self._phone_index.get(phone)
        return self.get(user_id) if user_id else None

    def find_by_email(self, email: str) -> User | None:
        user_id = self._email_index.get(email)
        return self.get(user_id) if user_id else None

    def find_by_wechat_open_id(self, open_id: str) -> User | None:
        user_id = self._wechat_index.get(open_id)
        return self.get(user_id) if user_id else None

    def find_by_weibo_open_id(self, open_id: str) -> User | None:
        user_id = self._weibo_index.get(open_id)
        return self.get(user_id) if user_id else None

    def _check_index_conflict(self, user: User) -> None:
        auth = user.auth
        if auth.phone:
            owner = self._phone_index.get(auth.phone)
            if owner and owner != user.id:
                raise ConflictError("phone already exists")
        if auth.email:
            owner = self._email_index.get(auth.email)
            if owner and owner != user.id:
                raise ConflictError("email already exists")
        if auth.wechat_open_id:
            owner = self._wechat_index.get(auth.wechat_open_id)
            if owner and owner != user.id:
                raise ConflictError("wechat account already exists")
        if auth.weibo_open_id:
            owner = self._weibo_index.get(auth.weibo_open_id)
            if owner and owner != user.id:
                raise ConflictError("weibo account already exists")

    def _refresh_indexes(self, user: User) -> None:
        self._remove_index_for_user(user.id)
        if user.auth.phone:
            self._phone_index[user.auth.phone] = user.id
        if user.auth.email:
            self._email_index[user.auth.email] = user.id
        if user.auth.wechat_open_id:
            self._wechat_index[user.auth.wechat_open_id] = user.id
        if user.auth.weibo_open_id:
            self._weibo_index[user.auth.weibo_open_id] = user.id

    def _remove_index_for_user(self, user_id: str) -> None:
        self._phone_index = {k: v for k, v in self._phone_index.items() if v != user_id}
        self._email_index = {k: v for k, v in self._email_index.items() if v != user_id}
        self._wechat_index = {k: v for k, v in self._wechat_index.items() if v != user_id}
        self._weibo_index = {k: v for k, v in self._weibo_index.items() if v != user_id}

