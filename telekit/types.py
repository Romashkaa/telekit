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
