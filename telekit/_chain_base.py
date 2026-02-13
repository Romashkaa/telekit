# Copyright (c) 2025 Ving Studio, Romashka
# Licensed under the MIT License. See LICENSE file for full terms.

# Standard library
import inspect
from typing import Callable

# Third-party packages
import telebot
from telebot.types import Message

# Local modules
from . import senders
from . import _input_handler
from . import _timeout

class ChainBase:

    bot: telebot.TeleBot

    _timeout_warnings_enabled: bool = True
    
    @classmethod
    def _init(cls, bot: telebot.TeleBot):
        """
        Initializes the bot instance for the class.

        Args:
            bot (TeleBot): The Telegram bot instance to be used for sending messages.
        """
        cls.bot = bot

    def __init__(self, chat_id: int, *, previous_message: Message | None = None):
        self.chat_id = chat_id
        self.sender = senders.AlertSender(chat_id)
        self._handler = _input_handler.InputHandler(chat_id)
        self._previous_message = previous_message
        self._timeout_handler = _timeout.TimeoutHandler()

        self.do_remove_timeout = True
        self.do_remove_entry_handler = True
        self.do_remove_inline_keyboard = True
    
    # -------------------------------------------
    # Cleanup Logic: manages clearing input handlers, inline keyboards, and timeout after each step
    # -------------------------------------------

    def _cancel_timeout_and_handlers(self):
        self._cancel_timeout()
        self._handler.reset()
        self._remove_all_handlers()
    
    # API
        
    def remove_timeout(self):
        """
        Forces the removal of the active timeout handler.

        This immediately clears any pending timeout to prevent it from triggering.

        You can also remove all handlers at once using `remove_all_handlers()`.
        """
        self._timeout_handler.remove()
    
    def remove_entry_handler(self):
        """
        Forces the removal of the current entry handler.

        This disables any active entry_* callbacks, 
        ensuring they won't process new incoming messages.

        You can also remove all handlers at once using `remove_all_handlers()`.
        """
        self._handler.set_entry_callback(None)

    def remove_inline_keyboard(self):
        """
        Forces the removal of the inline keyboard and all related callbacks.

        This clears both the visual buttons and their callback bindings.

        You can also remove all handlers at once using `remove_all_handlers()`.
        """
        self.sender.set_reply_markup(None)
        self._handler.set_button_callbacks(None)

    def remove_all_handlers(self):
        """
        Forces removal of all handlers associated with the chain.

        This includes timeouts, entry handlers, and inline keyboards.
        Use when starting a new chain to avoid conflicts with old state.

        This includes:
        - timeouts (`remove_timeout()`),
        - entry handlers (`remove_entry_handler()`), 
        - and inline keyboards (`remove_inline_keyboard()`).
        """
        self.remove_timeout()
        self.remove_entry_handler()
        self.remove_inline_keyboard()

    def _remove_all_handlers(self):
        if self.do_remove_timeout:
            self.remove_timeout()
        if self.do_remove_entry_handler:
            self.remove_entry_handler()
        if self.do_remove_inline_keyboard:
            self.remove_inline_keyboard()

    # Configuration API

    def set_remove_timeout(self, remove_timeout: bool = True):
        """
        Enables or disables automatic timeout removal after sending a message.

        When True, the timeout handler will be cleared after each message, 
        preventing it from triggering for every subsequent message.
        Set to False if you want to keep the same timeout across messages.
        """
        self.do_remove_timeout = remove_timeout

    def set_remove_entry_handler(self, remove_entry_handler: bool = True):
        """
        Enables or disables automatic removal of entry handlers after sending a message.

        When True, any entry_* handlers (like entry_text) will be cleared automatically 
        to avoid being reused unintentionally in the next message.
        Set to False if you need to persist them between messages.
        """
        self.do_remove_entry_handler = remove_entry_handler

    def set_remove_inline_keyboard(self, remove_inline_keyboard: bool = True):
        """
        Enables or disables automatic removal of the inline keyboard after sending a message.

        When True, the inline keyboard will be removed automatically 
        to prevent it from appearing in the next message by mistake.
        Set to False if you want to reuse the same keyboard in subsequent messages.
        """
        self.do_remove_inline_keyboard = remove_inline_keyboard

    def set_break_only_on_match(self, break_only_on_match: bool = True):
        """
        Sets whether the current chain should only be interrupted if the incoming 
        message matches another existing handler.

        :param break_only_on_match: If True, random messages that don't trigger any 
            handler will be ignored, keeping the chain active. If False, any message 
            will terminate the chain (if no active entry handler: `chain.set_entry...()`).
        :type break_only_on_match: `bool`
        """
        self._handler.break_only_on_match = break_only_on_match

    def set_break_on_commands(self, break_on_commands: bool = True):
        """
        Sets whether commands (messages starting with '/') should take priority over 
        the current entry handler.

        :param break_on_commands: If True, commands will always terminate the chain 
            and trigger the corresponding command handler. If False, commands will 
            be passed to the entry handler like regular text.
        :type break_on_commands: `bool`
        """
        self._handler.break_on_commands = break_on_commands
    
    # -------------------------------------------
    # Timeout Logic
    # -------------------------------------------

    def _set_timeout_callback(self, callback: Callable):
        def wrapper():
            self._handler.reset()
            callback()
        self._handler.set_cancel_timeout_callback(self._timeout_handler.cancel)
        self._timeout_handler.set_callback(wrapper)

    def _set_timeout_time(self, seconds: int=0, minutes: int=0, hours: int=0):
        self._timeout_handler.set_time(seconds, minutes, hours)
    
    def _start_timeout(self) -> bool:
        return self._timeout_handler.maybe_start()

    def _cancel_timeout(self):
        self._timeout_handler.cancel()

    # Timeout API

    def disable_timeout_warnings(self, value: bool = True) -> None:
        self._timeout_warnings_enabled = not value