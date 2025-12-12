from typing import Callable, Any
import inspect

import telebot
from telebot.types import Message

from .logger import logger
library = logger.library

from .chain import Chain
from .callback_query_handler import CallbackQueryHandler
from .user import User
from .on import On


class Handler:
    
    # Base Class Attributes
    bot: telebot.TeleBot

    # Subclas Attributes
    on:  On

    # Instance Attributes
    user: User
    chain: Chain
    message: Message

    # -----------------------------------------------------
    # Initialization of all Handlers
    # -----------------------------------------------------

    handlers: list[type['Handler']] = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Handler.handlers.append(cls)
    
    @classmethod
    def _init(cls, bot: telebot.TeleBot):
        """
        Initializes the bot instance for the handler class and sets up all registered handlers.

        For each subclass of Handler, this method attaches an On instance for message handling 
        and calls its `init_handler` method to register the message callbacks.

        Args:
            bot (TeleBot): The Telegram bot instance to be used for sending messages.
        """
        if cls is not Handler:
            raise RuntimeError("Do not call `Handler.init` on a subclass. Use the base Handler class only.")

        cls.bot = bot
        cls.handlers_dict = {}

        for handler in cls.handlers:
            handler.on = On(handler, bot)
            handler.init_handler()

            cls.handlers_dict[handler.__name__] = handler
    
    @classmethod
    def init_handler(cls) -> None:
        """
        Initializes the message handler. 
        You should redefine it in your handler class to add message handlers:

        ```python
        class HelpHandler(telekit.Handler):

            @classmethod
            def init_handler(cls) -> None:
                cls.on.message(commands=['help']).invoke(cls.handle_help)
        ```
        """
        pass

    # -----------------------------------------------------
    # Initialization of handlers Instances
    # -----------------------------------------------------

    def __init__(self, message: Message):
        self.message: Message = message
        self.user = User(self.message.chat.id, self.message.from_user)
        self.new_chain()

    def handle(self) -> Any:
        """
        Recommended method _(name)_ to serve as a unified entry point 
        for your handler. The library does not call this method automatically, 
        but having a single `handle` method is convenient when delegating 
        control to another handler via `handoff` or similar mechanisms. 

        Using one `handle` method to start processing the message 
        avoids the need for multiple custom entry methods 
        like `start` or `handle_start`.
        """
        library.warning("Handler `handle` was called but not overridden; no logic executed.")
        return

    # -----------------------------------------------------
    # Methods
    # -----------------------------------------------------

    def simulate_user_message(self, message_text: str) -> None:
        """
        Simulates a user sending a message to the bot.

        Useful for testing, triggering handlers programmatically, 
        or switching between commands without sending real Telegram messages.

        Args:
            message_text (str): The text of the message to simulate.

        Example:
            >>> self.simulate_user_message("/start")
        """
        CallbackQueryHandler().simulate(self.message, message_text)

    def delete_user_initial_message(self):
        self.chain.sender.delete_message(self.message)
    
    def new_chain(self):
        if hasattr(self, "chain"):
            del self.chain

        self.chain = Chain(self.message.chat.id)

    def get_local_chain(self) -> Chain:
        return Chain(self.message.chat.id)
    
    def handoff(self, handler: str | type["Handler"]) -> "Handler":
        if isinstance(handler, str):
            if handler in self.handlers_dict:
                handler = self.handlers_dict[handler]

        if not (isinstance(handler, type) and issubclass(handler, Handler)):
            raise TypeError(f"{type(self).__name__}().handoff(HERE) <- Expected `Handler` type")
        
        handler_instance = handler(self.message)
        handler_instance.chain._set_previous_message(self.chain.get_previous_message())
        
        return handler_instance
    
    def freeze(self, func, *args):
        """
        Return a zero-argument callback that invokes the given function
        with the provided arguments.

        Args:
            func (Callable): The function to be executed when the callback is triggered.
            *args: Arguments that will be passed to the function upon execution.

        Returns:
            Callable: A wrapper function that calls `func(*args)` when invoked.

        Example:
            >>> btn = self.freeze((lambda a, b: a + b), 2, 3)
            >>> btn() # 5
        """
        def wrapper():
            func(*args)

        return wrapper

def accepts_parameter(func: Callable) -> bool:
    """
    Checks if the function accepts at least one parameter,
    ignoring 'self' for class methods.
    """
    sig = inspect.signature(func)
    params = list(sig.parameters.values())

    if params and params[0].name == "cls":
        params = params[1:]

    return len(params) > 0
