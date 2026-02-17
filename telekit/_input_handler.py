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

from typing import Callable, Any

from telebot.types import Message
import telebot

from ._logger import logger
library = logger.library
from ._callback_query_handler import CallbackQueryHandler

class InputHandler:

    # class attributes
    bot: telebot.TeleBot

    # instance attributes
    break_only_on_match: bool
    break_on_commands: bool
    
    @classmethod
    def _init(cls, bot: telebot.TeleBot):
        """
        Initializes the bot instance for the class.

        Args:
            bot (TeleBot): The Telegram bot instance to be used for sending messages.
        """
        cls.bot = bot
        
    def __init__(self, chat_id: int):
        self.chat_id = chat_id
        self.button_callbacks: dict[str, Callable[[telebot.types.CallbackQuery], None]] | None = None
        self.entry_callback: Callable[[Message], bool] | None = None
        self.cancel_timeout_callback: Callable | None = None
        self.break_only_on_match: bool = True
        self.break_on_commands: bool = True

    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––
    # Configuration API
    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––

    # Timeout

    def reset(self):
        CallbackQueryHandler.remove_user_button_callbacks(self.chat_id)
        self.bot.clear_step_handler_by_chat_id(self.chat_id)

    def cancel_timeout(self):
        cancel_timeout_callback = self.__dict__["cancel_timeout_callback"]
        if cancel_timeout_callback:
            cancel_timeout_callback()

    def set_cancel_timeout_callback(self, callback: Callable[[], None] | None):
        self.cancel_timeout_callback = callback

    # Inline Keyboard

    def set_button_callbacks(self, button_callbacks: dict[str, Callable[[telebot.types.CallbackQuery], None]] | None) -> None:
        """
        Sets the callback functions for the inline keyboard buttons.

        Args:
            button_callbacks (`dict[str, Callable[[], Any]]`): A dictionary mapping callback data to functions.
        """
        self.button_callbacks = button_callbacks

        if not button_callbacks:
            CallbackQueryHandler.remove_user_button_callbacks(self.chat_id)

    # Message Handling

    def set_entry_callback(self, entry_callback: Callable[[Message], bool] | None) -> None:
        """
        Sets the callback functions for the input.

        Args:
            entry_callback (`dict[str, Callable[[Message], bool]]`): A function.
        """
        self.entry_callback = entry_callback

    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––
    # Handling API
    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––

    # Start Handling

    def handle_next_message(self) -> bool:
        """
        Registers a handler for the next user message (input).
        """
            
        self.bot.clear_step_handler_by_chat_id(self.chat_id)

        has_handlers: bool = bool(self.entry_callback) or bool(self.button_callbacks)

        if has_handlers:
            self.bot.register_next_step_handler_by_chat_id(self.chat_id, self._handle_entry)
        
        self._update_query_handler_callbacks()
        
        return has_handlers

    def _update_query_handler_callbacks(self):
        if self.button_callbacks:
            CallbackQueryHandler.set_user_button_callbacks(self.chat_id, self.button_callbacks)
        else:
            CallbackQueryHandler.remove_user_button_callbacks(self.chat_id)
    
    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––
    # Entry Handling
    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––

    def _handle_entry(self, message: Message):
        """
        Handles the next message by calling the appropriate callback based on the message data.
        """
        CallbackQueryHandler.remove_user_button_callbacks(self.chat_id)
        
        if self.break_on_commands and message.text and message.text.startswith("/"):
            self.cancel_timeout()
            self.bot.process_new_messages([message])
        elif self.entry_callback:
            if not self.entry_callback(message):
                self.handle_next_message()
        elif not self.break_only_on_match or self._has_message_handler(message):
            self.cancel_timeout()
            self.bot.process_new_messages([message])
        else:
            self.handle_next_message()
    
    def _has_message_handler(self, message) -> bool:
        """
        Checks if there is a handler in the bot that will accept this message.
        """
        for handler in self.bot.message_handlers:
            if self.bot._test_message_handler(handler, message):
                return True

        return False

