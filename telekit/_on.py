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

from typing import Callable
import typing
import shlex
import re

import telebot

from . import parameters
from ._logger import logger
library = logger.library

if typing.TYPE_CHECKING:
    from telekit._handler import Handler # only for type hints

# --------------------------------------------------------
# Event Handler
# --------------------------------------------------------

class Invoker:
    """
    • [See Documentation on GitHub](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/3_triggers.md)
    """

    def __init__(self, decorator: Callable[[Callable], Callable | None], handler: type["Handler"]):
        """
        Wraps an existing decorator (like cls.on_text) 
        to add callback/trigger functionality.
        """
        self._decorator: Callable = decorator
        self._Handler = handler

    def __call__(self, func: Callable):
        """Use as decorator.
        
        Example:
        ```
        @cls.on.command("help")
        def _handle(message: Message, *args, **kwargs):
            cls(message).handle(*args, **kwargs)
        ```
        """
        return self._decorator(func)

    def invoke(self, callback: Callable, pass_args: bool = True):
        """
        Assign a callback to be executed by this trigger.

        Example:
            >>> cls.on.command("help").invoke(cls.handle)
        """

        def handler(message, *args, **kwargs):
            if pass_args:
                callback(self._Handler(message), *args, **kwargs)
            else:
                callback(self._Handler(message))

        self._decorator(handler)

# --------------------------------------------------------
# On Handlers
# --------------------------------------------------------

class On:

    """
    • [See Documentation on GitHub](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/3_triggers.md)
    """

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
        Handles new incoming messages of any kind (text, photo, sticker, etc.). As a parameter to the decorator function, it passes a `telebot.types.Message` object. All message handlers are tested in the order they were added.

        • [See Documentation on GitHub](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/3_triggers.md)

        ---
        ## Example:
        ```
        class HelpHandler(telekit.Handler):
            @classmethod
            def init_handler(cls) -> None:
                cls.on.message(commands=['help']).invoke(cls.handle)

                # Or define the trigger manually:
                @cls.on.message(commands=['help'])
                def handler(message: telebot.types.Message) -> None:
                    cls(message).handle()
        ```
        ---

        Triggers:
            - By command(s) (via `commands` argument)
            - By regular expression (via `regexp` argument)
            - By custom filter function (via `func` argument)
            - By content type(s) (via `content_types` argument)

        Filters:
            - By whitelist (via `whitelist` argument)
            - By chat type(s) (via `chat_types` argument)
            - All filters supported by telebot.TeleBot.message_handler can be used via keyword arguments.

        Args:
            commands (list[str] | None): List of command strings (e.g., ['/start', '/help']) that trigger the handler.
            regexp (str | None): Regular expression string to match messages.
            func (Callable[..., Any] | None): Optional function to pass directly to the TeleBot decorator.
            content_types (list[str] | None): List of content types like ['text', 'photo', 'sticker'].
            chat_types (list[str] | None): List of chat types, e.g., ['private', 'group'].
            whitelist (list[int] | None): List of chat IDs allowed to trigger the handler.
            **kwargs: Any other keyword arguments supported by `telebot.TeleBot.message_handler`.

        Returns:
            Invoker: An invoker object allowing `.invoke()` or @decorator-style usage.
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
        Triggers when a message matches one or more text patterns.

        Patterns can include placeholders in curly braces (e.g., "My name is {name}"), 
        which will be captured as keyword arguments and passed to the handler function.

        • [See Documentation on GitHub](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/3_triggers.md)

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

        Triggers:
            - By matching one or more text patterns (with optional curly-brace placeholders)

        Filters:
            - Only messages of type "text" are considered.
            - By chat type(s) (via `chat_types` argument)
            - By whitelist (via `whitelist` argument)
            - Additional filters can be applied via chat_types and whitelist.

        Args:
            *patterns (str): One or more text patterns to match against incoming messages.
            chat_types (list[str] | None): List of chat types, e.g., ['private', 'group'].
            whitelist (list[int] | None): List of chat IDs allowed to trigger the handler.

        Returns:
            Invoker: An invoker object allowing `.invoke()` or decorator-style usage.
        """
        if patterns:
            compiled = []

            for p in patterns:
                # {name} -> (?P<name>.+)
                regex = re.sub(r"{(\w+)}", r"(?P<\1>.+)", p)
                compiled.append(re.compile(
                    f"^{regex}$",
                    re.IGNORECASE
                ))

            def _filter_func(message: telebot.types.Message) -> bool:
                if whitelist is not None and message.chat.id not in whitelist:
                    return False
                
                if not message.text:
                    return False
                
                for cregex in compiled:
                    match = cregex.match(message.text)
                    if match:
                        return True
                    
                return False

            def decorator(func: Callable):
                @self.bot.message_handler(func=_filter_func, chat_types=chat_types)
                def _(message):
                    for cregex in compiled:
                        match = cregex.match(message.text)
                        if match:
                            func(message, **match.groupdict())
                            return
                        
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
        Handles new incoming commands.

        • [See Documentation on GitHub](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/3_triggers.md)

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

        Triggers:
            - By command(s) (via `*commands` argument)

        Filters:
            - By chat type(s) (via `chat_types` argument)
            - By whitelist (via `whitelist` argument)
            - Additional filters can be applied via chat_types and whitelist.

        Args:
            *commands (str): List of command strings (e.g., ['start', 'help']) that trigger the handler.
            params (list[Parameter] | None): Optional list of parameter types to parse from the command arguments.
            chat_types (list[str] | None): List of chat types, e.g., ['private', 'group'].
            whitelist (list[int] | None): List of chat IDs allowed to trigger the handler.
            **kwargs: Any other keyword arguments supported by `telebot.TeleBot.message_handler`.

        Returns:
            Invoker: An invoker object allowing `.invoke()` or decorator-style usage.
        """
        original_decorator = self.bot.message_handler(
            commands=[c.lstrip("/") for c in commands],
            chat_types=chat_types,
            **kwargs
        )

        def decorator(handler: Callable[..., typing.Any]):
            def wrapped(message):
                if whitelist is not None and message.chat.id not in whitelist:
                    return
                if params:
                    return handler(message, *self._analyze_params(message.text, params))
                
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

        • [See Documentation on GitHub](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/3_triggers.md)

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

        Triggers:
            - By regular expression match (via `regexp` argument)

        Filters:
            - By chat type(s) (via `chat_types` argument)
            - By whitelist (via `whitelist` argument)
            - Additional filters can be applied via chat_types and whitelist.

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
        Handles new incoming photo messages. All message handlers are tested in the order they were added.

        • [See Documentation on GitHub](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/3_triggers.md)

        ---
        ## Example:
        ```
        class MyHandler(telekit.Handler):
            @classmethod
            def init_handler(cls) -> None:
                cls.on.photo().invoke(cls.handle)

                # Or define the handler manually:
                @cls.on.photo()
                def handler(message: telebot.types.Message) -> None:
                    cls(message).handle()
        ```
        ---

        Triggers:
            - By receiving a photo message (content_type="photo")

        Filters:
            - By chat type(s) (via `chat_types` argument)
            - By whitelist (via `whitelist` argument)
            - Additional filters can be applied via chat_types and whitelist.

        Args:
            chat_types (list[str] | None): List of chat types, e.g., ['private', 'group'].
            whitelist (list[int] | None): List of chat IDs allowed to trigger the handler.
            **kwargs: Any other keyword arguments supported by `telebot.TeleBot.message_handler`.

        Returns:
            Invoker: An invoker object allowing `.invoke()` or decorator-style usage.
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
    
    def func(
        self,
        func: Callable[[telebot.types.Message], bool],
        invoke_args: list | tuple | None = None,
        invoke_kwargs: dict[str, typing.Any] | None = None,
        chat_types: list[str] | None = None,
        whitelist: list[int] | None = None,
        **kwargs
    ):
        """
        Handles new incoming messages of any kind (text, photo, sticker, etc.) using a custom filter function. As a parameter to the decorator function, it passes a telebot.types.Message object. All message handlers are tested in the order they were added.

        • [See Documentation on GitHub](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/3_triggers.md)

        ---
        ## Example:
        ```
        class HelpHandler(telekit.Handler):
            @classmethod
            def init_handler(cls) -> None:
                cls.on.func(lambda m: m.text == "help").invoke(cls.handle)

                # Or define the handler manually:
                @cls.on.func(lambda m: m.text == "help")
                def handler(message: telebot.types.Message) -> None:
                    cls(message).handle()
        ```
        ---

        Triggers:
            - By custom filter function (via `func` argument, should return True for matching messages)

        Filters:
            - By chat type(s) (via `chat_types` argument)
            - By whitelist (via `whitelist` argument)
            - Additional filters can be applied via chat_types and whitelist.

        Args:
            func (Callable[[telebot.types.Message], bool]): Custom filter function that must return True for messages to trigger the handler.
            invoke_args (list | tuple | None): Optional positional arguments to pass to the handler function when invoked.
            invoke_kwargs (dict[str, Any] | None): Optional keyword arguments to pass to the handler function when invoked.
            chat_types (list[str] | None): List of chat types, e.g., ['private', 'group'].
            whitelist (list[int] | None): List of chat IDs allowed to trigger the handler.
            **kwargs: Any other keyword arguments supported by `telebot.TeleBot.message_handler`.

        Returns:
            Invoker: An invoker object allowing `.invoke()` or decorator-style usage.
        """

        def _filter(message):
            if whitelist is not None and message.chat.id not in whitelist:
                return False
            return bool(func(message))

        original_decorator = self.bot.message_handler(
            func=_filter,
            chat_types=chat_types,
            **kwargs
        )

        def decorator(handler: Callable[..., typing.Any]):
            if not invoke_args and not invoke_kwargs:
                return original_decorator(handler)

            def _wrap_args(message, *args, **kwargs):
                final_args = args
                final_kwargs = kwargs

                if invoke_args is not None:
                    final_args = invoke_args

                if invoke_kwargs is not None:
                    final_kwargs = invoke_kwargs

                return handler(message, *final_args, **final_kwargs)

            return original_decorator(_wrap_args)

        return Invoker(decorator, self.handler)