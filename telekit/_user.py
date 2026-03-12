# 
# Copyright (C) 2026 Romashka
# 
# This file is part of Telekit.
# 
# Telekit is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version.
# 
# Telekit is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty 
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See 
# the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License 
# along with Telekit. If not, see <https://www.gnu.org/licenses/>.
# 
from functools import cached_property
from typing import Literal

import telebot
import telebot.types

from ._logger import logger

__all__ = ["User"]


class User:

    bot: telebot.TeleBot

    @classmethod
    def _init(cls, bot: telebot.TeleBot) -> None:
        cls.bot = bot

    def __init__(self, message: telebot.types.Message) -> None:
        self._message = message
        self._chat_id = message.chat.id
        self.logger   = logger.users(self._chat_id)

    # ── sender ────────────────────────────────────────────────────

    @cached_property
    def _sender(self) -> telebot.types.User | telebot.types.Chat:
        return self._message.from_user or self._message.chat

    # ── logging ───────────────────────────────────────────────────

    def enable_logging(self, *user_ids: int | str) -> None:
        """Enable logging for this user or for additional user IDs."""
        logger.enable_user_logging(*(user_ids or (self._chat_id,)))

    # ── identity ──────────────────────────────────────────────────

    @cached_property
    def id(self) -> int:
        return self._sender.id

    @cached_property
    def is_bot(self) -> bool:
        if isinstance(self._sender, telebot.types.User):
            return self._sender.is_bot
        return False

    # ── name ──────────────────────────────────────────────────────

    @cached_property
    def first_name(self) -> str | None:
        if isinstance(self._sender, telebot.types.User):
            return self._sender.first_name
        return self._sender.first_name or self._sender.title

    @cached_property
    def last_name(self) -> str | None:
        return self._sender.last_name

    @cached_property
    def full_name(self) -> str | None:
        if isinstance(self._sender, telebot.types.User):
            return self._sender.full_name
        return " ".join(filter(None, [self.first_name, self.last_name])) or None
    
    @cached_property
    def username(self) -> str | None:
        return self._sender.username

    # ── locale ────────────────────────────────────────────────────

    @cached_property
    def language_code(self) -> str | None:
        if isinstance(self._sender, telebot.types.User):
            return self._sender.language_code
        return None

    # ── premium & extras ──────────────────────────────────────────

    @cached_property
    def is_premium(self) -> bool:
        if isinstance(self._sender, telebot.types.User):
            return bool(self._sender.is_premium)
        return False

    @cached_property
    def added_to_attachment_menu(self) -> bool:
        if isinstance(self._sender, telebot.types.User):
            return bool(self._sender.added_to_attachment_menu)
        return False

    # ── chat-only ─────────────────────────────────────────────────

    @cached_property
    def chat_type(self) -> Literal["private", "group", "supergroup", "channel"]:
        """Type of the chat: private, group, supergroup, or channel."""
        return self._message.chat.type # pyright: ignore[reportReturnType]