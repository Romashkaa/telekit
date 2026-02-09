# Copyright (c) 2025 Ving Studio, Romashka
# Licensed under the MIT License. See LICENSE file for full terms.

# Third-party packages
import telebot.types
from telebot.types import InlineKeyboardButton

__all__ = [
    "InlineButton", 

    "LinkButton", 
    "WebAppButton", 
    "SuggestButton",
    "CopyTextButton",
]

class InlineButton:
    """
    Base class for: 
    - `LinkButton` 
    - `WebAppButton`
    - `SuggestButton`
    - `CopyTextButton`
    """

    MAX_SIZE: int | None = None
    MIN_SIZE: int | None = None

    Link: type["LinkButton"]
    WebApp: type["WebAppButton"]
    Suggest: type["SuggestButton"]
    CopyText: type["CopyTextButton"]

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

    :param text: The suggestion text; 1-64 bytes
    :type text: `str`
    """

    MAX_SIZE: int | None = 64
    MIN_SIZE: int | None = 1

    def __init__(self, suggestion: str, strict: bool=True, **kwargs):
        self._suggestion = suggestion
        self._kwargs = kwargs

        if strict and not self._is_valid_telegram_callback(self._suggestion):
            raise ValueError(
                f"Callback data for SuggestButton() is too long! "
                f"Telegram limit is 1-64 bytes, but yours is {len(self._suggestion.encode('utf-8'))} bytes. "
                f"Suggestion: '{self._suggestion}'"
            )
        
    def _compile(self, caption: str) -> InlineKeyboardButton:
        return InlineKeyboardButton(
            text=caption,
            callback_data=self._suggestion
        )
    
InlineButton.Link = LinkButton
InlineButton.WebApp = WebAppButton
InlineButton.Suggest = SuggestButton
InlineButton.CopyText = CopyTextButton