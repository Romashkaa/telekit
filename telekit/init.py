from .handler import Handler
from .chain import Chain
from .input_handler import InputHandler
from .callback_query_handler import CallbackQueryHandler
from .user import User
from . import senders

import telebot  # type: ignore

__all__ = ["init"]

def init(bot: telebot.TeleBot) -> None:
    senders.BaseSender.init(bot)
    Handler.init(bot)
    Chain.init(bot)
    InputHandler.init(bot)
    CallbackQueryHandler.init(bot)
    User.init(bot)
