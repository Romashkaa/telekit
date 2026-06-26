from typing import Any

from telebot import TeleBot
from telebot.types import Message

import telekit
from telekit.styles import TextEntity, Escape, Raw, Group, Bold, Italic
from ._logger import _library

__all__ = ['Chat']

class Chat:

    bot: TeleBot

    @classmethod
    def _init(cls, bot: TeleBot):
        """
        Initializes the bot instance for the class.
        """
        cls.bot = bot

    def __init__(self, chat_id: int, thread_id: int | None = None, previous_user_message: Message | None = None) -> None:
        self.id = chat_id
        self.thread_id = thread_id
        self.previous_user_message = previous_user_message

    def _get_base_params(self) -> dict[str, Any]:
        return {
            "chat_id": self.id,
            "parse_mode": "html",
            "message_thread_id": self.thread_id
        }

    def answer(self, text: str | TextEntity):
        """
        Sends a text message to the chat.

        Returns:
            Message | None: The sent message or None if sending failed.
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
            _library.warning(f"^^^ [chat.answer]: Failed to answer (chat_id={self.id}; thread_id={self.thread_id}): {exception}")
            return None

    

    