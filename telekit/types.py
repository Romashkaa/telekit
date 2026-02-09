from enum import Enum

from ._chain import TextDocument
from ._user import User
from ._inline_buttons import (
    InlineButton, LinkButton, WebAppButton, CopyTextButton, SuggestButton
)

from .styles import Styles
from .senders import BaseSender

ChatAction = BaseSender.ChatAction
Effect = BaseSender.Effect

class ParseMode(str, Enum):
    HTML = "html"
    MARKDOWN = "markdown"

__all__ = [
    # Types / Dataclasses
    "TextDocument",
    "User",

    # Inline Buttons
    "InlineButton", 
    "LinkButton", 
    "WebAppButton", 
    "CopyTextButton",
    "SuggestButton",

    # Namespaces
    "Styles",
    
    # Enums
    "ChatAction",
    "Effect",
    "ParseMode",
]
