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

from typing import Any, Callable
from enum import Enum

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
    "CallbackButton",

    "ButtonStyle"
]

class ButtonStyle(Enum):
    DANGER  = "danger"
    SUCCESS = "success"
    PRIMARY = "primary"

_BUTTON_STYLES_LIST = [e.value for e in ButtonStyle]

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
    
    Styles: type[ButtonStyle] = ButtonStyle

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
    
    def _normalize_style(self, style: str | ButtonStyle | None) -> str | None:
        if style is None:
            return None
        if isinstance(style, ButtonStyle):
            return style.value
        if isinstance(style, str):
            normalized = style.lower()
            if normalized in _BUTTON_STYLES_LIST:
                return normalized
            raise ValueError(f"Unknown style: {style!r}. Must be one of {_BUTTON_STYLES_LIST}")
        raise TypeError(f"Style must be str, ButtonStyle, or None, got {type(style)}")

    
class LinkButton(InlineButton):
    """
    This object represents an inline keyboard button that opens a link.

    :param url: HTTP or tg:// URL to be opened when the button is pressed. Links tg://user?id= can be used to mention a user by their ID without using a username, if this is allowed by their privacy settings.
    :type url: `str`

    :param style: Style of the button. Must be one of `telekit.types.ButtonStyle.DANGER` (red), 
              `*.SUCCESS` (green) or `*.PRIMARY` (blue). 
              You can also pass these as string values: "danger", "success", "primary". 
              If omitted, an app-specific default style is used.
    :type style: `str`

    :param kwargs: Additional keyword arguments passed directly to `InlineKeyboardButton`.
    :type kwargs: `Any`
    """
    def __init__(self, url: str, *, style: str | None | ButtonStyle = None, **kwargs):
        self._url = url
        self._style = self._normalize_style(style)
        self._kwargs = kwargs

    def _compile(self, caption: str) -> InlineKeyboardButton:
        return InlineKeyboardButton(
            text=caption,
            url=self._url,
            style=self._style,
            **self._kwargs
        )
    
class WebAppButton(InlineButton):
    """
    This object represents an inline keyboard button that describes a Web App.

    :param url: An HTTPS URL of a Web App to be opened
    :type url: `str`

    :param style: Style of the button. Must be one of `telekit.types.ButtonStyle.DANGER` (red), 
              `*.SUCCESS` (green) or `*.PRIMARY` (blue). 
              You can also pass these as string values: "danger", "success", "primary". 
              If omitted, an app-specific default style is used.
    :type style: `str`

    :param kwargs: Additional keyword arguments passed directly to `InlineKeyboardButton`.
    :type kwargs: `Any`
    """
    def __init__(self, url: str, *, style: str | None | ButtonStyle = None, **kwargs):
        self._url = url
        self._style = self._normalize_style(style)
        self._kwargs = kwargs
        
    def _compile(self, caption: str) -> InlineKeyboardButton:
        return InlineKeyboardButton(
            text=caption,
            web_app=telebot.types.WebAppInfo(self._url),
            style=self._style,
            **self._kwargs
        )
    
class CopyTextButton(InlineButton):
    """
    This object represents an inline keyboard button that copies specified text to the clipboard.

    :param text: The text to be copied to the clipboard; 1-256 characters
    :type text: `str`

    :param style: Style of the button. Must be one of `telekit.types.ButtonStyle.DANGER` (red), 
              `*.SUCCESS` (green) or `*.PRIMARY` (blue). 
              You can also pass these as string values: "danger", "success", "primary". 
              If omitted, an app-specific default style is used.
    :type style: `str`

    :param kwargs: Additional keyword arguments passed directly to `InlineKeyboardButton`.
    :type kwargs: `Any`
    """

    MAX_SIZE: int | None = 256
    MIN_SIZE: int | None = 1

    def __init__(self, text: str, *, style: str | None | ButtonStyle = None, strict: bool=True, **kwargs):
        self._text = text
        self._style = self._normalize_style(style)
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
            copy_text=telebot.types.CopyTextButton(self._text),
            style=self._style,
            **self._kwargs
        )
    
class SuggestButton(InlineButton):
    """
    This object represents an inline keyboard button that simulates taht user sent the message.

    :param suggestion: The suggestion text; 1-64 bytes
    :type suggestion: `str`

    :param style: Style of the button. Must be one of `telekit.types.ButtonStyle.DANGER` (red), 
              `*.SUCCESS` (green) or `*.PRIMARY` (blue). 
              You can also pass these as string values: "danger", "success", "primary". 
              If omitted, an app-specific default style is used.
    :type style: `str`

    :param kwargs: Additional keyword arguments passed directly to `InlineKeyboardButton`.
    :type kwargs: `Any`
    """

    MAX_SIZE: int | None = 64
    MIN_SIZE: int | None = 1

    def __init__(self, suggestion: str, *, style: str | None | ButtonStyle = None, strict: bool=True, **kwargs):
        self._suggestion = CallbackQueryHandler.suggest(suggestion)
        self._style = self._normalize_style(style)
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
            callback_data=self._suggestion,
            style=self._style,
            **self._kwargs,
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

    :param style: Style of the button. Must be one of `telekit.types.ButtonStyle.DANGER` (red), 
              `*.SUCCESS` (green) or `*.PRIMARY` (blue). 
              You can also pass these as string values: "danger", "success", "primary". 
              If omitted, an app-specific default style is used.
    :type style: `str`

    :param kwargs: Additional keyword arguments passed directly to `InlineKeyboardButton`.
    :type kwargs: `Any`
    """

    class _CallbackInvoker:
        def __init__(
                self, 
                chain_callback: Callable[[], None],
                callback: Callable[..., Any], 

                pass_args: tuple | list | None = None, 
                pass_kwargs: dict[str, Any] | None = None, 

                answer_text: str | None = None,
                answer_as_alert: bool = True,

                style: str | None | ButtonStyle = None,

                kwargs: dict[str, Any] = {}
            ):
            self._callback = callback

            self._pass_args = pass_args
            self._pass_kwargs = pass_kwargs

            self._answer_text = answer_text
            self._answer_as_alert = answer_as_alert

            self._style = style

            self._kwargs = {"style": style} | kwargs
            
            self._chain_callback: Callable[[], None] = chain_callback

        def _invoke_chain_callback(self):
            self.__dict__["_chain_callback"]()

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

            style: str | None | ButtonStyle = None,

            **kwargs
        ):
        self._callback = callback

        self._pass_args = pass_args
        self._pass_kwargs = pass_kwargs

        self._answer_text = answer_text
        self._answer_as_alert = answer_as_alert

        self._style = self._normalize_style(style)

        self._kwargs = kwargs
        
    def build_invoker(self, chain_callback: Callable[[], None]) -> _CallbackInvoker:
        return self._CallbackInvoker(
            chain_callback=chain_callback,
            callback=self._callback,
            pass_args=self._pass_args,
            pass_kwargs=self._pass_kwargs,
            answer_text=self._answer_text,
            answer_as_alert=self._answer_as_alert,
            style=self._style,
            kwargs=self._kwargs
        )
    
    @classmethod
    def create_invoker(cls, callback: Callable[[], None], chain_callback: Callable[[], None]) -> _CallbackInvoker:
        return cls._CallbackInvoker(
            chain_callback=chain_callback,
            callback=callback,
        )
    
InlineButton.Link = LinkButton
InlineButton.WebApp = WebAppButton
InlineButton.Suggest = SuggestButton
InlineButton.CopyText = CopyTextButton
InlineButton.Callback = CallbackButton