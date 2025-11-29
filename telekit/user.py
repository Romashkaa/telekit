import telebot.types
import telebot

from .logger import logger

__all__ = ["User"]

class User:

    bot: telebot.TeleBot
    
    @classmethod
    def _init(cls, bot: telebot.TeleBot):
        """
        Initializes the bot instance for the class.

        Args:
            bot (TeleBot): The Telegram bot instance to be used for sending messages.
        """
        cls.bot = bot

    def __init__(self, chat_id: int, from_user: telebot.types.User | None):
        self.chat_id = chat_id
        self.from_user = from_user

        self._username: str | None = None
        self._first_name: str | None = None
        self._last_name: str | None = None
        self._full_name: str | None = None
        self._user_id: int | None = None
        self._user_obj: telebot.types.User | None = None

        self.logger = logger.users(self.chat_id)

    def enable_logging(self, *user_ids: int | str):
        """
        Enable logging for this user or for additional user IDs.

        If no arguments are passed, enables logging for this instance's chat_id.
        """
        if user_ids:
            logger.enable_user_logging(*user_ids)
        else:
            logger.enable_user_logging(self.chat_id)
    
    @property
    def user_obj(self) -> telebot.types.User | None:
        """Returns the raw telebot.types.User object for the user (all Telegram info)."""
        if self._user_obj:
            return self._user_obj
        try:
            if self.from_user:
                self._user_obj = self.from_user
            else:
                self._user_obj = self.bot.get_chat(self.chat_id)  # type: ignore
        except:
            return None
        return self._user_obj

    @property
    def username(self) -> str | None:
        """Returns the Telegram username (e.g., @username) or first name if username is missing."""
        if self._username:
            return self._username
        user = self.user_obj
        if user:
            if getattr(user, "username", None):
                self._username = f"@{user.username}"
            else:
                self._username = user.first_name
        return self._username

    @property
    def first_name(self) -> str | None:
        """Returns the first name of the user as registered in Telegram."""
        if self._first_name:
            return self._first_name
        user = self.user_obj
        if user and getattr(user, "first_name", None):
            self._first_name = user.first_name
        return self._first_name

    @property
    def last_name(self) -> str | None:
        """Returns the last name of the user as registered in Telegram (may be None)."""
        if self._last_name:
            return self._last_name
        user = self.user_obj
        if user and getattr(user, "last_name", None):
            self._last_name = user.last_name
        return self._last_name

    @property
    def full_name(self) -> str | None:
        """Returns the full name of the user (first name + last name if available)."""
        if self._full_name:
            return self._full_name
        first = self.first_name or ""
        last = self.last_name or ""
        self._full_name = f"{first} {last}".strip() or None
        return self._full_name

    @property
    def id(self) -> int | None:
        """Returns the Telegram user ID of the user."""
        if self._user_id:
            return self._user_id
        user = self.user_obj
        if user and getattr(user, "id", None):
            self._user_id = user.id
        return self._user_id