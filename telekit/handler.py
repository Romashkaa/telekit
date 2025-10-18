from typing import Callable
import re
import typing

from telebot.types import Message
import telebot

from .chain import Chain
from .user import User


class Handler:
    
    bot: telebot.TeleBot
    
    @classmethod
    def init(cls, bot: telebot.TeleBot):
        """
        Initializes the bot instance for the class.

        Args:
            bot (TeleBot): The Telegram bot instance to be used for sending messages.
        """
        cls.bot = bot

        for handler in cls.handlers:
            handler.init_handler(bot)

    @classmethod
    def init_handler(cls, bot: telebot.TeleBot) -> None:
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

    def delete_user_initial_message(self):
        self.chain.sender.delete_message(self.message)

    def __init__(self, message: Message):
        self.message: Message = message
        self.user = User(self.message.chat.id, self.message.from_user)
        
        self._chain_factory: Callable[[], Chain] = Chain.get_chain_factory(self.message.chat.id)
        self._children_factory: Callable[[Chain | None], Chain] = Chain.get_children_factory(self.message.chat.id)
        
        self.chain: Chain = self.get_chain()

    def get_chain(self) -> Chain:
        self.chain = self._chain_factory()
        return self.chain
    
    def get_child(self, parent: Chain | None = None) -> Chain:
        if parent is None:
            parent = self.chain

        self.chain = self._children_factory(self.chain)
        return self.chain

    handlers: list[type['Handler']] = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Handler.handlers.append(cls)