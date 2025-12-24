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
from . import input_handler
from . import timeout

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

    def __init__(self, chat_id: int):
        self.chat_id = chat_id
        self.sender = senders.AlertSender(chat_id)
        self.handler = input_handler.InputHandler(chat_id)
        self._previous_message: Message | None = None
        self._timeout_handler = timeout.TimeoutHandler()

        self.do_remove_timeout = True
        self.do_remove_entry_handler = True
        self.do_remove_inline_keyboard = True
    
    # -------------------------------------------
    # Cleanup Logic: manages clearing input handlers, inline keyboards, and timeout after each step
    # -------------------------------------------

    def _got_response_or_callback(self):
        self._cancel_timeout()
        self._remove_all_handlers()

    def _accepts_parameter(self, func: Callable) -> bool:
        """
        Checks if the function accepts at least one parameter,
        ignoring 'self' for class methods.
        """
        sig = inspect.signature(func)
        params = list(sig.parameters.values())

        if params and params[0].name == "self":
            params = params[1:]

        return len(params) > 0
    
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
        self.handler.set_entry_callback(None)

    def remove_inline_keyboard(self):
        """
        Forces the removal of the inline keyboard and all related callbacks.

        This clears both the visual buttons and their callback bindings.

        You can also remove all handlers at once using `remove_all_handlers()`.
        """
        self.sender.set_reply_markup(None)
        self.handler.set_callback_functions({})

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
    
    # -------------------------------------------
    # Timeout Logic
    # -------------------------------------------

    def _set_timeout_callback(self, callback: Callable):
        def wrapper():
            self.handler.reset()
            callback()
        self.handler.set_cancel_timeout_callback(self._timeout_handler.cancel)
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