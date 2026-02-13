# Copyright (c) 2025 Ving Studio, Romashka
# Licensed under the MIT License. See LICENSE file for full terms.

from typing import Any, Callable

# Third-party packages
import telebot.types
from telebot.types import InlineKeyboardButton, CallbackQuery
from telebot import TeleBot
from ._callback_query_handler import CallbackQueryHandler

__all__ = [
    "InlineButton", 

    "LinkButton", 
    "WebAppButton", 
    "SuggestButton",
    "CopyTextButton",

    "CallbackButton"
]

class InlineButton:

    """
    Base class for: 
    - `LinkButton` 
    - `WebAppButton`
    - `SuggestButton`
    - `CopyTextButton`
    - `CallbackButton`
    """

    _bot: TeleBot

    @classmethod
    def _init(cls, bot: TeleBot):
        cls._bot = bot

    MAX_SIZE: int | None = None
    MIN_SIZE: int | None = None

    Link: type["LinkButton"]
    WebApp: type["WebAppButton"]
    Suggest: type["SuggestButton"]
    CopyText: type["CopyTextButton"]
    Callback: type["CallbackButton"]

    def __init__(self):
        raise NotImplementedError()

    def _compile(self, caption: str) -> InlineKeyboardButton:
        raise NotImplementedError()
    
    def _is_valid_telegram_callback(self, data: str, encoding: str | None = "utf-8") -> bool:
        if encoding:
            size = len(data.encode(encoding))
        else:
            size = len(data)

        if self.MIN_SIZE is not None and size < self.MIN_SIZE:
            return False
        if self.MAX_SIZE is not None and size > self.MAX_SIZE:
            return False
        
        return True
    
class LinkButton(InlineButton):
    """
    This object represents an inline keyboard button that opens a link.

    :param url: HTTP or tg:// URL to be opened when the button is pressed. Links tg://user?id= can be used to mention a user by their ID without using a username, if this is allowed by their privacy settings.
    :type url: `str`

    :param kwargs: Additional keyword arguments passed directly to `InlineKeyboardButton`.
    :type kwargs: `Any`
    """
    def __init__(self, url: str, **kwargs):
        self._url = url
        self._kwargs = kwargs

    def _compile(self, caption: str) -> InlineKeyboardButton:
        return InlineKeyboardButton(
            text=caption,
            url=self._url,
            **self._kwargs
        )
    
class WebAppButton(InlineButton):
    """
    This object represents an inline keyboard button that describes a Web App.

    :param url: An HTTPS URL of a Web App to be opened
    :type url: `str`

    :param kwargs: Additional keyword arguments passed directly to `InlineKeyboardButton`.
    :type kwargs: `Any`
    """
    def __init__(self, url: str, **kwargs):
        self._url = url
        self._kwargs = kwargs
        
    def _compile(self, caption: str) -> InlineKeyboardButton:
        return InlineKeyboardButton(
            text=caption,
            web_app=telebot.types.WebAppInfo(self._url),
            **self._kwargs
        )
    
class CopyTextButton(InlineButton):
    """
    This object represents an inline keyboard button that copies specified text to the clipboard.

    :param text: The text to be copied to the clipboard; 1-256 characters
    :type text: `str`

    :param kwargs: Additional keyword arguments passed directly to `InlineKeyboardButton`.
    :type kwargs: `Any`
    """

    MAX_SIZE: int | None = 256
    MIN_SIZE: int | None = 1

    def __init__(self, text: str, strict: bool=True, **kwargs):
        self._text = text
        self._kwargs = kwargs

        if strict and not self._is_valid_telegram_callback(self._text, encoding=None):
            raise ValueError(
                f"Text for CopyTextButton() is too long! "
                f"Telegram limit is 1-256 characters, but yours is {len(self._text.encode('utf-8'))} bytes. "
                f"Suggestion: '{self._text}'"
            )
        
    def _compile(self, caption: str) -> InlineKeyboardButton:
        return InlineKeyboardButton(
            text=caption,
            copy_text=telebot.types.CopyTextButton(self._text)
        )
    
class SuggestButton(InlineButton):
    """
    This object represents an inline keyboard button that simulates taht user sent the message.

    :param suggestion: The suggestion text; 1-64 bytes
    :type suggestion: `str`

    :param kwargs: Additional keyword arguments passed directly to `InlineKeyboardButton`.
    :type kwargs: `Any`
    """

    MAX_SIZE: int | None = 64
    MIN_SIZE: int | None = 1

    def __init__(self, suggestion: str, strict: bool=True, **kwargs):
        self._suggestion = CallbackQueryHandler.suggest(suggestion)
        self._kwargs = kwargs
        
        if strict and not self._is_valid_telegram_callback(self._suggestion):
            raise ValueError(
                f"Callback data for SuggestButton() is too long! "
                f"Telegram limit is 1-64 bytes, but yours is {len(self._suggestion.encode('utf-8'))} bytes. "
                f"Suggestion: '{suggestion}'"
                f"Callback Data: '{self._suggestion}'"
            )
        
    def _compile(self, caption: str) -> InlineKeyboardButton:
        return InlineKeyboardButton(
            text=caption,
            callback_data=self._suggestion
        )
    
class CallbackButton(InlineButton):
    """
    This object represents an inline keyboard button that triggers a callback function when pressed.

    :param callback: A callable to be executed when the callback query is received.
    :type callback: `Callable[..., Any]`

    :param pass_args: Positional arguments to pass into the callback function.
    :type pass_args: `tuple | list | None`

    :param pass_kwargs: Keyword arguments to pass into the callback function.
    :type pass_kwargs: `dict[str, Any] | None`

    :param answer_text: Optional text to send as an answer to the callback query.
    :type answer_text: `str | None`

    :param answer_as_alert: If `True`, the answer text will be shown as an alert. If `False`, it will be shown as a notification at the top of the chat.
    :type answer_as_alert: `bool`

    :param kwargs: Additional keyword arguments passed directly to `InlineKeyboardButton`.
    :type kwargs: `Any`
    """

    class CallbackInvoker:
        def __init__(
                self, 
                chain_callback: Callable[[], None],
                callback: Callable[..., Any], 

                pass_args: tuple | list | None = None, 
                pass_kwargs: dict[str, Any] | None = None, 

                answer_text: str | None = None,
                answer_as_alert: bool = True,

                kwargs: dict[str, Any] = {}
            ):
            self._callback = callback

            self._pass_args = pass_args
            self._pass_kwargs = pass_kwargs

            self._answer_text = answer_text
            self._answer_as_alert = answer_as_alert

            self._kwargs = kwargs
            
            self._chain_callback: Callable[[], None] = chain_callback

        def _invoke_chain_callback(self):
            self.__dict__["_chain_callback"]()
            print("_chain_callback called")

        def _invoke_callback(self):
            args = self._pass_args or ()
            kwargs = self._pass_kwargs or {}
            self.__dict__["_callback"](*args, **kwargs)

        def _answer_callback_query(self, call: CallbackQuery):
            if self._answer_text:
                InlineButton._bot.answer_callback_query(
                    call.id, 
                    self._answer_text, 
                    self._answer_as_alert
                )

        def __call__(self, call: CallbackQuery):
            self._invoke_chain_callback()
            self._invoke_callback()
            self._answer_callback_query(call)

    def __init__(
            self, 
            callback: Callable[..., Any], 

            pass_args: tuple | list | None = None, 
            pass_kwargs: dict[str, Any] | None = None, 
            *,
            answer_text: str | None = None,
            answer_as_alert: bool = True,

            **kwargs
        ):
        self._callback = callback

        self._pass_args = pass_args
        self._pass_kwargs = pass_kwargs

        self._answer_text = answer_text
        self._answer_as_alert = answer_as_alert

        self._kwargs = kwargs
        
    def build_invoker(self, chain_callback: Callable[[], None]) -> CallbackInvoker:
        return self.CallbackInvoker(
            chain_callback=chain_callback,
            callback=self._callback,
            pass_args=self._pass_args,
            pass_kwargs=self._pass_kwargs,
            answer_text=self._answer_text,
            answer_as_alert=self._answer_as_alert,
            kwargs=self._kwargs
        )
    
    @classmethod
    def create_invoker(cls, callback: Callable[[], None], chain_callback: Callable[[], None]) -> CallbackInvoker:
        return cls.CallbackInvoker(
            chain_callback=chain_callback,
            callback=callback,
        )
    
InlineButton.Link = LinkButton
InlineButton.WebApp = WebAppButton
InlineButton.Suggest = SuggestButton
InlineButton.CopyText = CopyTextButton
InlineButton.Callback = CallbackButton