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
from dataclasses import dataclass

import telebot.types

from ._user import User
from ._inline_buttons import (
    InlineButton, 
    LinkButton, WebAppButton, 
    CopyTextButton, SuggestButton, 
    CallbackButton, 
    ButtonStyle
)

from .styles import Styles

class ParseMode(str, Enum):
    HTML = "html"
    MARKDOWN = "markdown"

class Effect(Enum):
    """
    Enum representing message effects:
    
    - FIRE - 🔥 
    - PARTY - 🎉 
    - HEART - ❤️ 
    - THUMBS_UP - 👍 
    - THUMBS_DOWN - 👎 
    - POOP - 💩 

    Use the `set_effect` method to use it
    """
    FIRE = "5104841245755180586"        # 🔥
    PARTY = "5046509860389126442"       # 🎉
    HEART = "5159385139981059251"       # ❤️
    THUMBS_UP = "5107584321108051014"   # 👍
    THUMBS_DOWN = "5104858069142078462" # 👎
    POOP = "5046589136895476101"        # 💩

    def __str__(self) -> str:
        return self.value
    
class ChatAction(Enum):
    """
    Represents chat actions (status indicators) that a bot can send,
    e.g., 'typing', 'upload_document', 'record_voice', etc.
    """
    TYPING = "typing"
    UPLOAD_PHOTO = "upload_photo"
    UPLOAD_DOCUMENT = "upload_document"
    UPLOAD_AUDIO = "upload_audio"
    UPLOAD_VIDEO = "upload_video"
    RECORD_VIDEO = "record_video"
    RECORD_VOICE = "record_voice"
    UPLOAD_VOICE = "upload_voice"
    CHOOSE_STICKER = "choose_sticker"
    FIND_LOCATION = "find_location"
    RECORD_VIDEO_NOTE = "record_video_note"
    UPLOAD_VIDEO_NOTE = "upload_video_note"

    def __str__(self) -> str:
        return self.value
    
@dataclass
class TextDocument:
    message: telebot.types.Message
    document: telebot.types.Document
    file_name: str
    encoding: str
    text: str

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
    "CallbackButton",

    "ButtonStyle",

    # Namespaces
    "Styles",
    
    # Enums
    "ChatAction",
    "Effect",
    "ParseMode",
]
