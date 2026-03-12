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
        self._message: telebot.types.Message = message
        self._chat_id: int = message.chat.id
        self.logger = logger.users(self._chat_id)

    # ── Internal ──────────────────────────────────────────────────

    @cached_property
    def _sender(self) -> telebot.types.User | telebot.types.Chat:
        """Resolves to `from_user` if available, otherwise falls back to `chat`."""
        return self._message.from_user or self._message.chat

    # ── Logging ───────────────────────────────────────────────────

    def enable_logging(self, *user_ids: int | str) -> None:
        """
        Enable logging for this user or for additional user IDs.
        If no arguments are passed, enables logging for this instance's chat ID.
        """
        logger.enable_user_logging(*(user_ids or (self._chat_id,)))

    # ── Telegram native fields ────────────────────────────────────

    @property
    def id(self) -> int:
        """Unique identifier of the user or chat."""
        return self._sender.id

    @property
    def username(self) -> str | None:
        """Telegram username without the leading `@`, or `None` if not set."""
        return self._sender.username

    @cached_property
    def first_name(self) -> str | None:
        """First name of the user, or the group/channel title as a fallback."""
        if isinstance(self._sender, telebot.types.User):
            return self._sender.first_name
        return self._sender.first_name or self._sender.title

    @property
    def last_name(self) -> str | None:
        """Last name of the user, or `None` for chats and users without one."""
        return self._sender.last_name

    @cached_property
    def is_bot(self) -> bool:
        """Whether the sender is a bot. Always `False` for chats."""
        if isinstance(self._sender, telebot.types.User):
            return self._sender.is_bot
        return False

    @cached_property
    def language_code(self) -> str | None:
        """
        IETF language code of the user's Telegram client (e.g. `"en"`, `"uk"`).
        Always `None` for chats.
        """
        if isinstance(self._sender, telebot.types.User):
            return self._sender.language_code
        return None

    @cached_property
    def is_premium(self) -> bool:
        """Whether the user has an active Telegram Premium subscription.
        Always `False` for chats and bots.
        """
        if isinstance(self._sender, telebot.types.User):
            return bool(self._sender.is_premium)
        return False

    @cached_property
    def added_to_attachment_menu(self) -> bool:
        """Whether this bot has been added to the user's attachment menu.
        Always `False` for chats.
        """
        if isinstance(self._sender, telebot.types.User):
            return bool(self._sender.added_to_attachment_menu)
        return False

    @property
    def chat_type(self) -> Literal["private", "group", "supergroup", "channel"]:
        """Type of the chat the message was sent in."""
        return self._message.chat.type  # pyright: ignore[reportReturnType]

    @property
    def bio(self) -> str | None:
        """Bio of the user or description of the chat, as set in Telegram."""
        return self._message.chat.bio

    @property
    def birthdate(self) -> telebot.types.Birthdate | None:
        """Birthdate of the user, if set and visible."""
        return self._message.chat.birthdate

    @property
    def description(self) -> str | None:
        """Description of the group or channel. `None` for private chats."""
        return self._message.chat.description

    # ── Computed helpers ──────────────────────────────────────────

    @cached_property
    def full_name(self) -> str | None:
        """Full name of the user (`first_name + last_name`), or the chat title.
        Returns `None` if neither is available.
        """
        if isinstance(self._sender, telebot.types.User):
            return self._sender.full_name
        return " ".join(filter(None, [self.first_name, self.last_name])) or None

    @property
    def mention(self) -> str:
        """
        A `tg://user?id=` deep link that mentions the user in any context,
        even without a username.
        """
        return f"tg://user?id={self.id}"

    @property
    def is_private(self) -> bool:
        """Whether the message was sent in a private chat."""
        return self.chat_type == "private"

    @property
    def is_group(self) -> bool:
        """Whether the message was sent in a group chat."""
        return self.chat_type == "group"

    @property
    def is_supergroup(self) -> bool:
        """Whether the message was sent in a supergroup."""
        return self.chat_type == "supergroup"

    @property
    def is_channel(self) -> bool:
        """Whether the message was sent in a channel."""
        return self.chat_type == "channel"

    @property
    def avatar(self) -> str | None:
        """
        File ID of the user's most recent profile photo, or `None` if not set.
        Makes an API call each time — cache the result if called frequently.
        """
        photos = self.bot.get_user_profile_photos(self.id, limit=1)
        if photos.total_count == 0:
            return None
        return photos.photos[0].file_id

    @property
    def profile_photos_count(self) -> int:
        """
        Total number of profile photos the user has set.
        Makes an API call each time.
        """
        return self.bot.get_user_profile_photos(self.id).total_count

    # ── Dunder ────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return f"User(id={self.id}, username={self.username!r})"