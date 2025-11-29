from typing import Callable, Any
from telebot.types import Message
import telebot

from .logger import logger
library = logger.library

class InputHandler:

    bot: telebot.TeleBot
    
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
        self.callback_functions: dict[str, Callable[..., Any]] = {}
        self.entry_callback: Callable[[Message], bool] | None = None
        self.cancel_timeout_callback: Callable | None = None

    def reset(self):
        self.bot.clear_step_handler_by_chat_id(self.chat_id)

    def cancel_timeout(self):
        cancel_timeout_callback = self.__dict__["cancel_timeout_callback"]
        if cancel_timeout_callback:
            cancel_timeout_callback()

    def set_cancel_timeout_callback(self, callback: Callable[[], None] | None):
        self.cancel_timeout_callback = callback

    def set_callback_functions(self, callback_functions: dict[str, Callable[[Message], Any]]) -> None:
        """
        Sets the callback functions for the inline keyboard buttons.

        Args:
            callback_functions (dict[str, Callable[[], Any]]): A dictionary mapping callback data to functions.
        """
        self.callback_functions = callback_functions

    def set_entry_callback(self, entry_callback: Callable[[Message], bool] | None) -> None:
        """
        Sets the callback functions for the input.

        Args:
            set_entry_callback (dict[str, Callable[[], Any]]): A function.
        """
        self.entry_callback = entry_callback

    def handle_next_message(self) -> bool:
        def handler(message: Message) -> None:
            if self.callback_functions:
                self.handle_callback(message)
            elif self.entry_callback:
                self.handle_entry(message)
            else:
                return
            
        self.bot.clear_step_handler_by_chat_id(self.chat_id)
        
        if self.callback_functions or self.entry_callback:
            self.bot.register_next_step_handler_by_chat_id(self.chat_id, handler)
            return True
        
        return False

    def handle_callback(self, message: Message) -> None:
        """
        Handles the next message by calling the appropriate callback based on the message data.
        """
        if message.text in self.callback_functions:
            self.cancel_timeout()
            callback = self.callback_functions[message.text]
            callback(message)
        elif message.text and message.text.startswith("/"):
            self.cancel_timeout()
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
            self.cancel_timeout()
            self.bot.process_new_messages([message])
        elif self.entry_callback:
            if not self.entry_callback(message):
                self.handle_next_message()
        else:
            self.handle_next_message()

