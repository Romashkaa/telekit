# Copyright (c) 2025 Ving Studio, Romashka
# Licensed under the MIT License. See LICENSE file for full terms.

from typing import Callable
import typing
import shlex
import re

import telebot

from . import parameters
from .logger import logger
library = logger.library

if typing.TYPE_CHECKING:
    from handler import Handler # only for type hints

# --------------------------------------------------------
# Event Handler
# --------------------------------------------------------

class Invoker:
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

        def handler(message, *args, **kwargs):
            if pass_args:
                callback(self._handler(message), *args, **kwargs)
            else:
                callback(self._handler(message))

        self._decorator(handler)

# --------------------------------------------------------
# On Handlers
# --------------------------------------------------------

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

        Args:
            commands (list[str] | None): List of command strings (e.g., ['/start', '/help']) that trigger the handler.
            regexp (str | None): Regular expression string to match messages.
            func (Callable[..., Any] | None): Optional function to pass directly to the TeleBot decorator.
            content_types (list[str] | None): List of content types like ['text', 'photo', 'sticker'].
            chat_types (list[str] | None): List of chat types, e.g., ['private', 'group'].
            whitelist (list[int] | None): List of chat IDs allowed to trigger the handler.
            **kwargs: Any other keyword arguments supported by `telebot.TeleBot.message_handler`.
        """
        original_decorator = self.bot.message_handler(
            commands=commands,
            regexp=regexp,
            func=func,
            content_types=content_types,
            chat_types=chat_types,
            **kwargs
        )

        def decorator(handler: Callable[..., typing.Any]):
            def wrapped(message):
                if whitelist is not None and message.chat.id not in whitelist:
                    return
                return handler(message)

            return original_decorator(wrapped)

        return Invoker(decorator, self.handler)

    def text(
            self, 
            *patterns: str, 
            chat_types: list[str] | None = None,
            whitelist: list[int] | None = None
        ):
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
            chat_types (list[str] | None): List of chat types, e.g., ['private', 'group'].
            whitelist (list[int] | None): List of chat IDs allowed to trigger the handler.

        Returns:
            Callable: A decorator that registers the message handler.
        """
        if patterns:
            regexes = []
            for p in patterns:
                # {name} -> (?P<name>.+)
                regex = re.sub(r"{(\w+)}", r"(?P<\1>.+)", p)
                regexes.append(f"^{regex}$")
            big_pattern = "|".join(regexes)

            def decorator(func: Callable):
                @self.bot.message_handler(regexp=big_pattern, chat_types=chat_types)
                def _(message):
                    if whitelist is not None and message.chat.id not in whitelist:
                        return
                    text = message.text
                    for regex in regexes:
                        match = re.match(regex, text)
                        if match:
                            func(message, **match.groupdict())
                            break
                return func
        else:
            def decorator(func: Callable):
                @self.bot.message_handler(content_types=["text"], chat_types=chat_types)
                def _(message):
                    if whitelist is not None and message.chat.id not in whitelist:
                        return
                    func(message)
                return func
        return Invoker(decorator, self.handler)
    
    def command(
        self,
        *commands: str,
        params: list[parameters.Parameter] | None=None,
        chat_types: list[str] | None = None,
        whitelist: list[int] | None = None,
        **kwargs
    ):
        """
        Handles new incoming commands. All message handlers are tested in the order they were added.

        ---
        ## Example:
        ```
        class MyHandler(telekit.Handler):
            @classmethod
            def init_handler(cls) -> None:
            
                cls.on.command("help").invoke(cls.handle)
            
                # Or define the handler manually:
            
                @cls.on.command("help")
                def handler(message: telebot.types.Message) -> None:
                    cls(message).handle()
        ```

        ---

        Args:
            *commands (str): List of command strings (e.g., ['start', 'help']) that trigger the handler.
            chat_types (list[str] | None): List of chat types, e.g., ['private', 'group'].
            whitelist (list[int] | None): List of chat IDs allowed to trigger the handler.
        """
        original_decorator = self.bot.message_handler(
            commands=list(commands),
            chat_types=chat_types,
            **kwargs
        )

        def decorator(handler: Callable[..., typing.Any]):
            def wrapped(message):
                if whitelist is not None and message.chat.id not in whitelist:
                    return
                if params:
                    return handler(message, *self._analyze_params(message.text, params))
                else:
                    return handler(message)

            return original_decorator(wrapped)

        return Invoker(decorator, self.handler)
    
    def _analyze_params(self, text: str, types: list[parameters.Parameter]) -> list:
        values: list[str] = shlex.split(text)[1:] # skip the command name
        args: list = []

        for i, ptype in enumerate(types):
            if len(values) <= i:
                break
            
            args.append(ptype(values[i]))

        return args
       
    def regexp(
        self,
        regexp: str,
        chat_types: list[str] | None = None,
        whitelist: list[int] | None = None,
        **kwargs
    ):
        """
        Registers a handler that triggers when an incoming message matches the given regular expression.

        ---
        ## Example:
        ```
        class MyHandler(telekit.Handler):
            @classmethod
            def init_handler(cls) -> None:
                cls.on.regexp(r"^\\d+$").invoke(cls.handle)

                # Or define the handler manually:
                @cls.on.regexp(r"^\\d+$")
                def handler(message: telebot.types.Message) -> None:
                    cls(message).handle()
        ```
        ---

        Args:
            regexp (str): Regular expression that must match the message text.
            chat_types (list[str] | None): Optional list of allowed chat types (e.g., ['private', 'group']).
            whitelist (list[int] | None): Optional list of chat IDs allowed to trigger this handler.
            **kwargs: Additional arguments passed to `telebot.message_handler`.

        Returns:
            Invoker: An invoker object allowing `.invoke()` or decorator-style usage.
        """
        original_decorator = self.bot.message_handler(
            regexp=regexp,
            chat_types=chat_types,
            **kwargs
        )

        def decorator(handler: Callable[..., typing.Any]):
            def wrapped(message):
                if whitelist is not None and message.chat.id not in whitelist:
                    return
                return handler(message)

            return original_decorator(wrapped)

        return Invoker(decorator, self.handler)
    
    def photo(
        self,
        chat_types: list[str] | None = None,
        whitelist: list[int] | None = None,
        **kwargs
    ):
        """
        Handles new incoming commands. All message handlers are tested in the order they were added.

        ---
        ## Example:
        ```
        class MyHandler(telekit.Handler):
            @classmethod
            def init_handler(cls) -> None:
            
                cls.on.command("help").invoke(cls.handle)
            
                # Or define the handler manually:
            
                @cls.on.command("help")
                def handler(message: telebot.types.Message) -> None:
                    cls(message).handle()
        ```

        ---

        Args:
            *commands (str): List of command strings (e.g., ['start', 'help']) that trigger the handler.
            chat_types (list[str] | None): List of chat types, e.g., ['private', 'group'].
            whitelist (list[int] | None): List of chat IDs allowed to trigger the handler.
        """
        original_decorator = self.bot.message_handler(
            content_types=["photo"],
            chat_types=chat_types,
            **kwargs
        )

        def decorator(handler: Callable[..., typing.Any]):
            def wrapped(message):
                if whitelist is not None and message.chat.id not in whitelist:
                    return
                return handler(message)

            return original_decorator(wrapped)

        return Invoker(decorator, self.handler) 