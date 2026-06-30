from typing import Any
from telebot import TeleBot
from telebot.types import Message, ReplyParameters
from telekit.styles import TextEntity, Escape
from ._logger import _library

__all__ = ['Chat']


class Chat:
    bot: TeleBot

    @classmethod
    def _init(cls, bot: TeleBot) -> None:
        cls.bot = bot

    def __init__(self, chat_id: int, thread_id: int | None = None, initial_user_message: Message | None = None) -> None:
        """
        Represents a chat (or a specific thread within a chat) that messages can be sent to.

        :param chat_id: The Telegram chat ID.
        :param thread_id: The message thread ID, if the chat is a forum topic.
            Defaults to ``None``.
        :param initial_user_message: The original user message that triggered this chat context,
            used as the target for :meth:`reply`. Defaults to ``None``.
        """
        self.id = chat_id
        self.thread_id = thread_id
        self.initial_user_message = initial_user_message

    def _get_base_params(self) -> dict[str, Any]:
        """
        Builds the base set of parameters shared by outgoing requests.

        :return: A dictionary with ``chat_id``, ``parse_mode``, and ``message_thread_id``.
        :rtype: dict[str, Any]
        """
        return {
            "chat_id": self.id,
            "parse_mode": "html",
            "message_thread_id": self.thread_id
        }

    def answer(self, text: str | TextEntity):
        """
        Sends a simple text message to the chat.

        :param text: The message content. Plain strings are HTML-escaped automatically;
            pass a ``TextEntity`` (e.g. ``Bold``, ``Italic``) for custom formatting.
        :return: The sent message, or ``None`` if sending failed.
        :rtype: Message | None
        """
        if not isinstance(text, TextEntity):
            text = Escape(text)

        try:
            return self.bot.send_message(
                chat_id           = self.id,
                message_thread_id = self.thread_id,
                text              = text.html,
                parse_mode        = "html",
            )
        except Exception as exception:
            text.debug("html")
            _library.warning(f"^^^ [chat.answer]: Failed to send message (chat_id={self.id}; thread_id={self.thread_id}): {exception}")
            return None

    def reply(self, text: str | TextEntity):
        """
        Sends a simple text message to the chat as a reply to the user's initial message.

        :param text: The message content. Plain strings are HTML-escaped automatically;
            pass a ``TextEntity`` (e.g. ``Bold``, ``Italic``) for custom formatting.
        :return: The sent message, or ``None`` if sending failed.
        :rtype: Message | None
        """
        if not isinstance(text, TextEntity):
            text = Escape(text)

        try:
            return self.bot.send_message(
                chat_id           = self.id,
                message_thread_id = self.thread_id,
                text              = text.html,
                parse_mode        = "html",
                reply_parameters  = self._get_reply_parameters()
            )
        except Exception as exception:
            text.debug("html")
            _library.warning(f"^^^ [chat.reply]: Failed to send message (chat_id={self.id}; thread_id={self.thread_id}, reply_parameters={self._get_reply_parameters()}): {exception}")
            return None

    def _get_reply_parameters(self) -> ReplyParameters | None:
        """
        Builds reply parameters pointing to the initial user message, if any.

        :return: ``ReplyParameters`` referencing :attr:`initial_user_message`, or ``None``
            if no initial message was provided.
        :rtype: ReplyParameters | None
        """
        return ReplyParameters(self.initial_user_message.message_id) if self.initial_user_message else None