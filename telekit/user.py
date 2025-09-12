import telebot.types # type: ignore
import telebot # type: ignore

# from cachetools import TTLCache

# cache: TTLCache[int, str] = TTLCache(maxsize=float("inf"), ttl=300)


class User:

    bot: telebot.TeleBot
    
    @classmethod
    def init(cls, bot: telebot.TeleBot):
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

    def get_username(self) -> str | None:
        if self._username:
            return self._username

        try:
            if self.from_user:
                user = self.from_user
            else:
                user = self.bot.get_chat(self.chat_id) # type: ignore

            if hasattr(user, "username") and user.username:
                self._username = f"@{user.username}"
            else:
                self._username = user.first_name
        except:
            return None

        return self._username