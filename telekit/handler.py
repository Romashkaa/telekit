from typing import Callable
import typing
import re

import inspect

from telebot.types import Message
import telebot

from .chain import Chain
from .callback_query_handler import CallbackQueryHandler
from .user import User

from .logger import logger
library = logger.library


class EventHandler:
    def __init__(self, decorator: Callable[[Callable], Callable | None], handler: type["Handler"]):
        """
        Wraps an existing decorator (like cls.on_text) 
        to add callback/trigger functionality.
        """
        self._decorator: Callable = decorator
        self._handler = handler

    def __call__(self, func: Callable):
        """Use as decorator"""
        return self._decorator(func)

    def invoke(self, callback: Callable, pass_args: bool = True):
        """
        Assign a callback to be executed by this handler.

        Example:
            >>> cls.on.command("help").invoke(cls.handle)
        """

        def handler(message, *args):
            if pass_args:
                callback(self._handler(message), *args)
            else:
                callback(self._handler(message))

        self._decorator(handler)

class On:

    bot: telebot.TeleBot
    handler: type["Handler"]

    def __init__(self, handler: type["Handler"], bot: telebot.TeleBot):
        """
        Initializes the bot instance for the class.
        """
        self.handler = handler
        self.bot = bot

    def message(
        self,
        commands: list[str] | None = None,
        regexp: str | None = None,
        func: Callable[..., typing.Any] | None = None,
        content_types: list[str] | None = None,
        chat_types: list[str] | None = None,
        whitelist: list[int] | None = None,
        **kwargs
    ):
        """
        Handles New incoming message of any kind - text, photo, sticker, etc. As a parameter to the decorator function, it passes telebot.types.Message object. All message handlers are tested in the order they were added.

        ---
        ## Example:
        ```
        class HelpHandler(telekit.Handler):
            @classmethod
            def init_handler(cls) -> None:
            
                cls.on.message(commands=['help']).invoke(cls.handle)
            
                # Or define the handler manually:
            
                @cls.on.message(commands=['help'])
                def handler(message: telebot.types.Message) -> None:
                    cls(message).handle()
        ```
        ---
        """
        original_decorator = self.bot.message_handler(
            commands=commands,
            regexp=regexp,
            func=func,
            content_types=content_types,
            chat_types=chat_types,
            **kwargs
        )

        def wrapper(handler: Callable[..., typing.Any]):
            def wrapped(message, *args, **kw):
                if whitelist is not None and message.chat.id not in whitelist:
                    return
                return handler(message, *args, **kw)

            return original_decorator(wrapped)

        return EventHandler(wrapper, self.handler)

    def text(self, *patterns: str):
        """
        Decorator for registering a handler that triggers when a message matches one or more text patterns.

        Patterns can include placeholders in curly braces (e.g., "My name is {name}"), 
        which will be captured as keyword arguments and passed to the handler function.

        ---
        ## Example:
        ```
        class NameHandler(telekit.Handler):
            @classmethod
            def init_handler(cls) -> None:
            
                cls.on.text("My name is {name}", "I am {name}").invoke(cls.handle_name)
            
                # Or define the handler manually:
            
                @cls.on.text("My name is {name}", "I am {name}")
                def handle_name(message, name: str):
                    cls(message).handle_name(name)
        ```
        ---

        Args:
            *patterns (str): One or more text patterns to match against incoming messages.

        Returns:
            Callable: A decorator that registers the message handler.
        """
        regexes = []
        for p in patterns:
            # {name} -> (?P<name>.+)
            regex = re.sub(r"{(\w+)}", r"(?P<\1>.+)", p)
            regexes.append(f"^{regex}$")
        big_pattern = "|".join(regexes)

        def decorator(func: Callable):
            @self.bot.message_handler(regexp=big_pattern)
            def _(message):
                text = message.text
                for regex in regexes:
                    match = re.match(regex, text)
                    if match:
                        func(message, **match.groupdict())
                        break
            return func
        return EventHandler(decorator, self.handler)

class Handler:
    
    bot: telebot.TeleBot
    on:  On
    
    @classmethod
    def init(cls, bot: telebot.TeleBot):
        """
        Initializes the bot instance for the class.

        Args:
            bot (TeleBot): The Telegram bot instance to be used for sending messages.
        """
        cls.bot = bot

        for handler in cls.handlers:
            handler.on = On(handler, bot)

            if accepts_parameter(handler.init_handler):
                library.warning(
                    f"[DEPRECATED] {handler.__name__}.init_handler(bot) "
                    f"was called from {__file__}. This method signature "
                    f"is deprecated and will be removed soon. "
                    f"Use 'cls.bot' or Telekit handlers "
                    f"(e.g., cls.handle_message(...)) instead."
                )
                handler.init_handler(bot) # type: ignore
            else:
                handler.init_handler()
    
    @classmethod
    def init_handler(cls) -> None:
        """
        Initializes the message handler
        """
        pass

    @classmethod
    def message_handler(
        cls,
        commands: list[str] | None = None,
        regexp: str | None = None,
        func: Callable[..., typing.Any] | None = None,
        content_types: list[str] | None = None,
        chat_types: list[str] | None = None,
        whitelist: list[int] | None = None,
        **kwargs
    ):
        """
        DEPRECATED: This API is deprecated and will be removed soon.
        Use '@cls.on.message(...)' or '@cls.bot.message_handler(...)' instead.

        ---

        Handles New incoming message of any kind - text, photo, sticker, etc. As a parameter to the decorator function, it passes telebot.types.Message object. All message handlers are tested in the order they were added.

        ---
        ## Example:
        ```
        class HelpHandler(telekit.Handler):
            @classmethod
            def init_handler(cls) -> None:
            
                @cls.message_handler(commands=['help'])
                def handler(message: telebot.types.Message) -> None:
                    cls(message).handle()
        ```
        ---
        """
        library.warning(
            f"[DEPRECATED] {cls.__name__}.message_handler is deprecated and will be removed soon. "
            f"Use '@cls.on.message(...)' or '@cls.bot.message_handler(...)' instead."
        )

        original_decorator = cls.bot.message_handler(
            commands=commands,
            regexp=regexp,
            func=func,
            content_types=content_types,
            chat_types=chat_types,
            **kwargs
        )

        def wrapper(handler: Callable[..., typing.Any]):
            def wrapped(message, *args, **kw):
                if whitelist is not None and message.chat.id not in whitelist:
                    return
                return handler(message, *args, **kw)

            return original_decorator(wrapped)

        return wrapper


    @classmethod
    def on_text(cls, *patterns: str):
        """
        DEPRECATED: This API is deprecated and will be removed soon.
        Use '@cls.on.text(...)' instead.

        ---

        Decorator for registering a handler that triggers when a message matches one or more text patterns.

        Patterns can include placeholders in curly braces (e.g., "My name is {name}"), 
        which will be captured as keyword arguments and passed to the handler function.

        ---
        ## Example:
        ```
        class NameHandler(telekit.Handler):
            @classmethod
            def init_handler(cls) -> None:
            
                @cls.on_text("My name is {name}", "I am {name}")
                def handle_name(message, name: str):
                    cls(message).handle_name(name)
        ```
        ---

        Args:
            *patterns (str): One or more text patterns to match against incoming messages.

        Returns:
            Callable: A decorator that registers the message handler.
        """
        library.warning(
            f"[DEPRECATED] {cls.__name__}.on_text is deprecated and will be removed soon. "
            f"Use '@cls.on.text(...)' instead."
        )
        
        regexes = []
        for p in patterns:
            # {name} -> (?P<name>.+)
            regex = re.sub(r"{(\w+)}", r"(?P<\1>.+)", p)
            regexes.append(f"^{regex}$")
        big_pattern = "|".join(regexes)

        def decorator(func: Callable):
            @cls.bot.message_handler(regexp=big_pattern)
            def _(message):
                text = message.text
                for regex in regexes:
                    match = re.match(regex, text)
                    if match:
                        func(message, **match.groupdict())
                        break
            return func
        return decorator

    def __init__(self, message: Message):
        self.message: Message = message
        self.user = User(self.message.chat.id, self.message.from_user)
        
        self._chain_factory: Callable[[], Chain] = Chain.get_chain_factory(self.message.chat.id)
        self._children_factory: Callable[[Chain | None], Chain] = Chain.get_children_factory(self.message.chat.id)
        
        self.chain: Chain = self.get_chain()

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

    def get_chain(self) -> Chain:
        self.chain = self._chain_factory()
        return self.chain
    
    def get_child(self, parent: Chain | None = None) -> Chain:
        if parent is None:
            parent = self.chain

        self.chain = self._children_factory(parent)
        return self.chain

    handlers: list[type['Handler']] = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Handler.handlers.append(cls)

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
