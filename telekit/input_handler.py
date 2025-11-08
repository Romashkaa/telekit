from operator import call
from typing import Callable, Any
from telebot.types import Message
import telebot

import inspect

class InputHandler:

    bot: telebot.TeleBot
    
    @classmethod
    def init(cls, bot: telebot.TeleBot):
        """
        Initializes the bot instance for the class.

        Args:
            bot (TeleBot): The Telegram bot instance to be used for sending messages.
        """
        cls.bot = bot
        
    def __init__(self, chat_id: int):
        self.chat_id = chat_id
        self.callback_functions: dict[str, Callable[..., Any]] = {}
        self.entry_callback: Callable[[Message], bool] | None = None

    def set_callback_functions(self, callback_functions: dict[str, Callable[[Message], Any]]) -> None:
        """
        Sets the callback functions for the inline keyboard buttons.

        Args:
            callback_functions (dict[str, Callable[[], Any]]): A dictionary mapping callback data to functions.
        """
        self.callback_functions = callback_functions

    def set_entry_callback(self, entry_callback: Callable[[Message], bool]) -> None:
        """
        Sets the callback functions for the input.

        Args:
            set_entry_callback (dict[str, Callable[[], Any]]): A function.
        """
        self.entry_callback = entry_callback

    def handle_next_message(self) -> None:
        def handler(message: Message) -> None:
            if self.callback_functions:
                self.handle_callback(message)
            elif self.entry_callback:
                self.handle_entry(message)
            else:
                return
        
        if self.callback_functions or self.entry_callback:
            self.bot.register_next_step_handler_by_chat_id(self.chat_id, handler)

    def handle_callback(self, message: Message) -> None:
        """
        Handles the next message by calling the appropriate callback based on the message data.
        """
        if message.text in self.callback_functions:
            callback = self.callback_functions[message.text]
            if self.accepts_parameter(callback):
                callback(message)
            else:
                callback()
        elif message.text and message.text.startswith("/"):
            self.bot.process_new_messages([message])
        elif self.entry_callback:
            self.handle_entry(message)
        else:
            self.handle_next_message()

    def handle_entry(self, message: Message):
        """
        Handles the next message by calling the appropriate callback based on the message data.
        """
        if message.text and message.text.startswith("/"):
            self.bot.process_new_messages([message])
        elif self.entry_callback:
            if not self.entry_callback(message):
                self.handle_next_message()
        else:
            self.handle_next_message()

    def accepts_parameter(self, func: Callable) -> bool:
        """
        Checks if the function accepts at least one parameter,
        ignoring 'self' for class methods.
        """
        sig = inspect.signature(func)
        params = list(sig.parameters.values())

        if params and params[0].name == "self":
            params = params[1:]

        return len(params) > 0

