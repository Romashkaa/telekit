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

from .utils import format_file_size

from ._user import User
from ._inline_buttons import (
    InlineButton, 
    LinkButton, WebAppButton, 
    CopyTextButton, SuggestButton, 
    CallbackButton, 
    ButtonStyle
)

from .styles import Styles, TextEntity, StaticTextEntity, EasyTextEntity

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
    """
    Represents a Telegram text document with decoded content
    and metadata.

    This object wraps a Telegram ``Document`` and provides
    convenient access to its size and formatted size.

    :param message: Original Telegram message containing the document.
    :type message: `telebot.types.Message`

    :param document: Telegram document object.
    :type document: `telebot.types.Document`

    :param file_name: Name of the uploaded file.
    :type file_name: `str`

    :param encoding: Text encoding used to decode the file.
    :type encoding: `str`

    :param text: Decoded text content of the document.
    :type text: `str`
    """
    message: telebot.types.Message
    document: telebot.types.Document
    file_name: str
    encoding: str
    text: str

    def format_size(self, precision: int = 1) -> str | None: 
        """
        Return the document size formatted as a human-readable string.

        Uses binary units (1 KB = 1024 bytes) via ``telekit.utils.format_file_size()``.

        :param precision: Number of decimal places for fractional values.
            Ignored if the value is an integer after conversion.
            Default is 1.
        :type precision: `int`

        :return: Formatted file size (e.g., ``"1.5 MB"``),
            or ``None`` if the document size is unavailable.
        :rtype: `str | None`

        Examples:

            >>> doc.format_size()
            '2.3 MB'

            >>> doc.format_size(precision=2)
            '2.35 MB'
        """
        return format_file_size(self.size, precision=precision) if self.size else None

    @property
    def formatted_size(self) -> str | None: 
        """
        Return the document size formatted as a human-readable string.

        Uses binary units (1 KB = 1024 bytes) via ``self.format_size(precision=1)``.

        Examples:

            >>> doc.formatted_size
            '2 MB'
        """
        return self.format_size()
    
    @property
    def size(self) -> int | None:
        return self.document.file_size

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

    # Styles
    "Styles",
    "TextEntity",
    "StaticTextEntity",
    "EasyTextEntity",
    
    # Enums
    "ChatAction",
    "Effect",
    "ParseMode",
]
