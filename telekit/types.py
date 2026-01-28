from enum import Enum

from ._chain import TextDocument
from ._user import User

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

    # Namespaces
    "Styles",
    
    # Enums
    "ChatAction",
    "Effect",
    "ParseMode",
]
