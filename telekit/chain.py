# Copyright (c) 2025 Ving Studio, Romashka
# Licensed under the MIT License. See LICENSE file for full terms.

# Standard library
from typing import Callable

# Third-party packages
import telebot
from telebot.types import Message

# Local modules
from . import senders

# Logging
from .logger import logger
library = logger.library

# Chain modules
from .chain_inline_keyboards_logic import ChainInlineKeyboardLogic
from .chain_entry_logic import ChainEntryLogic, TextDocument

__all__ = ["TextDocument", "Chain"]


class Chain(ChainInlineKeyboardLogic, ChainEntryLogic):

    bot: telebot.TeleBot

    # -------------------------------------------
    # Timeouts API
    # -------------------------------------------

    def on_timeout(self, seconds: int = 0, minutes: int = 0, hours: int = 0):
        """
        Decorator for registering a callback to be executed after a timeout.

        Sets a timeout for the user's response (inline keyboard or entry_*). 

        After the specified duration, the callback will be executed if the user hasn't responded.

        ---

        ## Usage:
        ```
            @chain.on_timeout(seconds=10)
            def my_callback():
                ...
        ```
        ---
        
        """
        def decorator(func: Callable[[], None]):
            self.set_timeout(func, seconds=seconds, minutes=minutes, hours=hours)
            return func
        return decorator
    
    def set_timeout(self, callback: Callable[[], None] | None, seconds: int=0, minutes: int=0, hours: int=0):
        """
        Sets a timeout callback for the user's response (inline keyboard or entry_*). 

        After the specified duration, the callback will be executed if the user hasn't responded.

        Args:
            callback (Callable[[], None] | None): The function to call after the timeout. If None, a no-op is used.
            seconds (int, optional): Number of seconds to wait before executing the callback. Defaults to 0.
            minutes (int, optional): Number of minutes to wait before executing the callback. Defaults to 0.
            hours (int, optional): Number of hours to wait before executing the callback. Defaults to 0.

        Notes:
            - The timeout will be scheduled relative to the current `chain.send()` or `chain.edit()` execution.
        """
        if callback is None:
            callback = lambda: None
        self._set_timeout_callback(callback)
        self._set_timeout_time(seconds, minutes, hours)

    def set_default_timeout(self, seconds: int=90, message: str="\n\nLooks like things went quiet... The session has ended."):
        """
        Sets a default timeout for user inactivity.

        If the user does not interact with the bot within the specified time,
        the session is gracefully closed: the current message is updated, and the timeout message is appended at the end.
        All active handlers are cleared, and the chain state is updated.

        Args:
            seconds (int, optional): Number of seconds to wait before triggering the timeout.
                Defaults to 90.
            message (str, optional): Message shown to the user when the timeout occurs.
                Defaults to a friendly inactivity notice.

        Notes:
            - The timeout is bound to the current chain lifecycle.
            - All active input handlers are removed once the timeout is triggered.
        """
        def timeout_handler():
            self.sender.add_message(message)
            self.remove_all_handlers()
            self.edit()
        
        self.set_timeout(timeout_handler, seconds)

    # -------------------------------------------
    # Sending & Editing API
    # -------------------------------------------
    
    def send(self) -> Message | None:
        """
        Sends a new message or edits the previous message if enabled.

        >>> self.chain.send()

        Returns:
            Message | None: The sent or edited message.
        """
        self.sender.set_edit_message(None)
        return self._send()
    
    def edit(self) -> Message | None:
        """
        Edits the previously sent message.

        >>> self.chain.edit()

        Returns:
            Message | None: The edited message.
        """
        self.mark_previous_message_for_edit()
        return self._send()
    
    def __call__(self, *args):
        self.send()
    
    def _send(self)  -> Message | None:
        _timeout = self._start_timeout()
        _handler = self.handler.handle_next_message()

        message = self.sender.send_or_handle_error()

        # reset edit target and store new previous message
        self.sender.set_edit_message(None)
        self._previous_message = message

        if self._timeout_warnings_enabled and _handler and not _timeout:
            library.warning(
                "Next-message handler is active, but no timeout was set for the chain. "
                "This may cause the bot to wait indefinitely."
            )

        return message
    
    def _set_previous_message(self, message: Message | None) -> None:
        self._previous_message = message

    # -------------------------------------------
    # Getters & Configuration
    # -------------------------------------------
    
    def get_previous_message(self) -> Message | None:
        """
        Returns the previous message sent by the chain.

        >>> self.chain.get_previous_message()
        
        Returns:
            Message | None: The previous message or None if no message was sent
        """
        if self._previous_message:
            return self._previous_message
        else:
            return None
        
    def mark_previous_message_for_edit(self) -> None:
        """
        Marks the previous message sent by the chain to be edited
        with the current sender's message when chain.send() is called.

        >>> self.chain.mark_previous_message_for_edit()

        is equivalent to:

        >>> self.chain.sender.set_edit_message(self.get_previous_message())
        """
        self.sender.set_edit_message(self.get_previous_message())
    
    def get_bot(self) -> telebot.TeleBot:
        """
        Returns the bot instance associated with this chain.
        
        Returns:
            telebot.TeleBot: The bot instance.
        """
        return self.bot
    
    def create_sender(self, chat_id: int | None=None) -> senders.AlertSender:
        if not chat_id:
            chat_id = self.chat_id
        return senders.AlertSender(chat_id)