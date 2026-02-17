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

from ._handler import Handler
from ._chain import Chain
from ._input_handler import InputHandler
from ._callback_query_handler import CallbackQueryHandler
from ._inline_buttons import InlineButton
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
    InlineButton._init(bot)
    User._init(bot)
