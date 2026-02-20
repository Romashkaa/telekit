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

import telebot.types
import telebot

from ._logger import logger

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

    # Chat Full Info

    def get_chat_full_info(self) -> telebot.types.ChatFullInfo | None:
        try:
            return self.bot.get_chat(self.chat_id)
        except:
            return None
        
    @property
    def chat_full_info(self) -> telebot.types.ChatFullInfo | None:
        # Equivalent to `get_chat_full_info()` but the result is cached so only one API call is needed.
        if not hasattr(self, "_chat_full_info"):
            self._chat_full_info = self.get_chat_full_info()
        
        return self._chat_full_info

    # Username

    def get_username(self) -> str | None:
        if chat := self.get_chat_full_info():
            return chat.username
    
    @property
    def username(self) -> str | None:
        if not hasattr(self, "_username"):
            self._username = self.get_username()
        
        return self._username
    
    # First Name

    def get_first_name(self) -> str | None:
        if chat := self.get_chat_full_info():
            return chat.first_name
    
    @property
    def first_name(self) -> str | None:
        if not hasattr(self, "_first_name"):
            self._first_name = self.get_first_name()
        
        return self._first_name
    
    # Last Name

    def get_last_name(self) -> str | None:
        if chat := self.get_chat_full_info():
            return chat.last_name
    
    @property
    def last_name(self) -> str | None:
        if not hasattr(self, "_last_name"):
            self._last_name = self.get_last_name()
        
        return self._last_name
    
    # Full Name

    def get_full_name(self) -> str | None:
        if chat := self.from_user: # TODO
            return chat.full_name
    
    @property
    def full_name(self) -> str | None:
        if not hasattr(self, "_full_name"):
            self._full_name = self.get_full_name()
        
        return self._full_name
    
    # User ID

    def get_id(self) -> int | None:
        if chat := self.from_user: # TODO
            return chat.id # TODO
    
    @property
    def id(self) -> int | None:
        if not hasattr(self, "_id"):
            self._id = self.get_id()
        
        return self._id