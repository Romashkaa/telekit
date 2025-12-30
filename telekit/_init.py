from ._handler import Handler
from ._chain import Chain
from ._input_handler import InputHandler
from ._callback_query_handler import CallbackQueryHandler
from ._user import User
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
