from typing import Any

import telebot # type: ignore
from telebot.types import ( # type: ignore
    Message, 
    InaccessibleMessage,
    CallbackQuery
)


class CallbackQueryHandler:

    bot: telebot.TeleBot
    
    @classmethod
    def init(cls, bot: telebot.TeleBot):
        """
        Initializes the bot instance for the class.

        Args:
            bot (TeleBot): The Telegram bot instance to be used for sending messages.
        """
        cls.bot = bot

        @bot.callback_query_handler(func=lambda call: True) # type: ignore
        def handle_callback(call: telebot.types.CallbackQuery) -> None: # type: ignore
            CallbackQueryHandler().handle(call)

    def handle(self, call: CallbackQuery):
        self._simulate(call.message, str(call.data), from_user=call.from_user)

    def _simulate(self, message: Message | InaccessibleMessage, text: str, from_user: Any=None) -> None:
        args = {}

        is_bot: bool = getattr(getattr(message, "from_user", from_user), "is_bot", False)

        args["message_id"]  = getattr(message, "message_id", None)
        args["from_user"]   = from_user if from_user else getattr(message, "from_user", None)
        args["date"]        = getattr(message, "date", None)
        args["chat"]        = getattr(message, "chat", None)
        args["json_string"] = getattr(message, "json", None)

        args["content_type"] = "text"
        args["options"]      = {}

        if any(value is None for value in args.values()): # type: ignore
            return print("Error: Missing required fields in message simulation.")
        
        original_message = message

        message = Message(**args) # type: ignore
        message.message_thread_id = getattr(original_message, "message_thread_id", None)
        message.text = text

        if message.from_user:
            message.from_user.is_bot = is_bot

        self.bot.process_new_messages([message]) # type: ignore
