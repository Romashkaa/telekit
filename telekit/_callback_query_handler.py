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

from typing import Any, Callable

import telebot
from telebot.types import (
    Message, 
    InaccessibleMessage,
    CallbackQuery
)


class CallbackQueryHandler:

    bot: telebot.TeleBot
    
    @classmethod
    def _init(cls, bot: telebot.TeleBot):
        """
        Initializes the bot instance for the class.

        Args:
            bot (TeleBot): The Telegram bot instance to be used for sending messages.
        """
        cls.bot = bot
        cls.user_button_callbacks: dict[int, dict[str, Callable[[telebot.types.CallbackQuery], None]]] = {}

        @bot.callback_query_handler(func=lambda call: True)
        def handle(call: telebot.types.CallbackQuery) -> None:
            if not call.data:
                return
            
            if call.data.startswith(cls.INLINE_BUTTON):
                cls._handle_inline_button(call)
            elif call.data.startswith(cls.SUGGEST):
                cls._handle_suggestion(call)
            else:
                cls.bot.answer_callback_query(call.id, text=cls._invalid_data_answer[0], show_alert=cls._invalid_data_answer[1])

    # –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    # Inline Buttons Handling
    # –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

    @classmethod
    def _handle_inline_button(cls, call: telebot.types.CallbackQuery):
        if not call.data:
            cls.bot.answer_callback_query(call.id, text=cls._invalid_data_answer[0], show_alert=cls._invalid_data_answer[1])
            return
        
        button_callbacks: dict[str, Callable] | None = cls.user_button_callbacks.get(call.from_user.id)

        if not button_callbacks:
            cls.bot.answer_callback_query(call.id, text=cls._button_is_no_active_answer[0], show_alert=cls._button_is_no_active_answer[1])
            return
        
        callback: Callable | None = button_callbacks.get(call.data)

        if callback is None:
            cls.bot.answer_callback_query(call.id, text=cls._button_is_no_active_answer[0], show_alert=cls._button_is_no_active_answer[1])
            return

        cls.remove_user_button_callbacks(call.from_user.id)
        
        callback(call)

    # –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    # Suggestion Handling
    # –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

    @classmethod
    def _handle_suggestion(cls, call: CallbackQuery):
        text: str = str(call.data)[len(cls.SUGGEST):]
        cls.simulate(call.message, text, from_user=call.from_user)
        cls.bot.answer_callback_query(call.id)

    @classmethod
    def simulate(cls, message: Message | InaccessibleMessage, text: str, from_user: Any=None) -> None:
        """
        Internal API method
        """
        args = {}

        is_bot: bool = getattr(getattr(message, "from_user", from_user), "is_bot", False)

        args["message_id"]  = getattr(message, "message_id", None)
        args["from_user"]   = from_user if from_user else getattr(message, "from_user", None)
        args["date"]        = getattr(message, "date", None)
        args["chat"]        = getattr(message, "chat", None)
        args["json_string"] = getattr(message, "json", None)

        args["content_type"] = "text"
        args["options"]      = {}

        if any(value is None for value in args.values()):
            raise ValueError("Missing required fields in message simulation.")
        
        original_message = message

        message = Message(**args)
        message.message_thread_id = getattr(original_message, "message_thread_id", None)
        message.text = text

        if message.from_user:
            message.from_user.is_bot = is_bot

        cls.bot.process_new_messages([message])

    # –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    # Query Types
    # –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

    INLINE_BUTTON: str = "inline_button:"
    SUGGEST: str = "suggest:"

    @classmethod
    def suggest(cls, suggestion: str):
        return f"{cls.SUGGEST}{suggestion}"
    
    @classmethod
    def inline_button(cls, button_id: str):
        return f"{cls.INLINE_BUTTON}{button_id}"
    
    # –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    # Internal API
    # –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

    @classmethod
    def set_user_button_callbacks(cls, chat_id: int, user_button_callbacks: dict[str, Callable]):
        """
        Internal API method
        """
        cls.user_button_callbacks[chat_id] = user_button_callbacks

    @classmethod
    def remove_user_button_callbacks(cls, chat_id: int):
        """
        Internal API method
        """
        cls.user_button_callbacks.pop(chat_id, None)

    @classmethod
    def has_user_button_callbacks(cls, chat_id: int) -> bool:
        """
        Internal API method
        """
        return not not cls.user_button_callbacks.get(chat_id)
    
    # –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    # Answers
    # –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    
    # (text: str, is_alert: bool)

    _invalid_data_answer: tuple[str, bool] = ("Invalid Call Data (None)", True)
    _button_is_no_active_answer: tuple[str, bool] = ("Button is no longer active", True)

    @classmethod
    def set_invalid_data_answer(cls, answer: str="Invalid Call Data (None)", is_alert: bool=True):
        """
        Sets the response message and type for cases when the received callback data is invalid or empty.

        :param answer: The text message to be displayed to the user.
        :type answer: `str`
        :param is_alert: Whether to show the message as a popup alert or a small notification.
        :type is_alert: `bool`
        """
        cls._invalid_data_answer = (answer, is_alert)

    @classmethod
    def set_button_is_no_active_answer(cls, answer: str="Button is no longer active", is_alert: bool=True):
        """
        Sets the response message and type for cases when the user clicks an expired inline button.

        :param answer: The text message to be displayed to the user.
        :type answer: `str`
        :param is_alert: Whether to show the message as a popup alert or a small notification.
        :type is_alert: `bool`
        """
        cls._button_is_no_active_answer = (answer, is_alert)
