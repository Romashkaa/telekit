from .handler import Handler
from .chain import Chain
from .input_handler import InputHandler
from .callback_query_handler import CallbackQueryHandler
from .user import User
from .senders import BaseSender

import telebot

__all__ = ["init"]

def init(bot: telebot.TeleBot) -> None:
    BaseSender._init(bot)
    Handler._init(bot)
    Chain._init(bot)
    InputHandler._init(bot)
    CallbackQueryHandler._init(bot)
    User._init(bot)
