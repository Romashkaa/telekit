# Copyright (c) 2025 Ving Studio, Romashka
# Licensed under the MIT License. See LICENSE file for full terms.

from typing import Any
from enum import Enum
from telebot import TeleBot
from telebot.types import (
    Message, InputMediaPhoto, InputFile, InputMediaAudio, InputMediaDocument, InputMediaVideo
)

from .logger import logger
library = logger.library

from telekit.styles import NoSanitize, StyleFormatter, Composite, Styles

# ---------------------------------------------------------------------------------
# Temporary Messages Manager
# ---------------------------------------------------------------------------------

class TemporaryMsgStore:

    _temporary_messages: dict[int, set[int]] = {}

    @classmethod
    def add_temporary(cls, chat_id: int, message_id: int):
        if chat_id not in cls._temporary_messages:
            cls._temporary_messages[chat_id] = {message_id}
        else:
            messages: set[int] | None = cls._temporary_messages.get(chat_id, None)

            if messages is not None:
                messages.add(message_id)

    @classmethod
    def remove_temporary(cls, bot: TeleBot, chat_id: int):
        user_temps = cls._temporary_messages.get(chat_id, None)

        if user_temps:
            try:
                for _id in user_temps:
                    cls.delete(bot, chat_id, _id)

                cls._temporary_messages.pop(chat_id, None)
            except:
                pass

    @classmethod
    def delete(cls, bot: TeleBot, chat_id: int, message_id: int) -> bool:
        try:
            return bot.delete_message(chat_id, message_id)
        except:
            return False
    
    @classmethod
    def debug(cls, chat_id: int | None=None) -> dict[str, int]:
        return {
            "v.all_temps": len(cls._temporary_messages),
            "v.user_temps": len(cls._temporary_messages.get(chat_id, "")) # type: ignore
        }

# ---------------------------------------------------------------------------------
# Base Sender
# ---------------------------------------------------------------------------------

class BaseSender:

    bot: TeleBot

    @classmethod
    def _init(cls, bot: TeleBot):
        """
        Initializes the bot instance for the class.

        Args:
            bot (TeleBot): The Telegram bot instance to be used for sending messages.
        """
        cls.bot = bot

    def __init__(self,
                 chat_id: int,

                 text: str       = "",
                 reply_markup = None, # type: ignore

                 is_temporary: bool   = False,
                 delele_temporaries: bool = True,
                 
                 parse_mode: str | None = None,
                 reply_to_message_id: int | None = None,

                 edit_message_id: int | None = None,

                 thread_id: int | None = None,
                 effect_id: str | None = None,

                 photo: str | None = None
                 ):
        """
        Initializes the BaseSender object with message details.

        Args:
            chat_id (int): The ID of the chat to send messages to.
            text (str): The text of the message. Default is an empty string.
            reply_markup: Optional markup for adding inline buttons or keyboards.
            is_temp (bool): Whether the message is temporary. Default is False.
            del_temps (bool): Whether to delete temporary messages. Default is True.
            parse_mode (str): Parse mode for message formatting. Default is 'HTML'.
            reply_to_message_id (int): Optional ID of a message to reply to.
            edit_message_id (int): Optional ID of the message to edit.
        """
        self.chat_id = chat_id
        
        self.text = text
        self.reply_markup = reply_markup # type: ignore
        
        self.is_temporary = is_temporary
        self.delele_temporaries = delele_temporaries

        self.parse_mode = parse_mode
        self.reply_to_message_id = reply_to_message_id

        self.edit_message_id = edit_message_id

        self.thread_id = thread_id
        self.message_effect_id = effect_id

        self.photo = photo

        self.styles = Styles()

        self.media = []

        if self.parse_mode:
            self.styles.set_parse_mode(self.parse_mode)

    class Effect(Enum):
        FIRE = "5104841245755180586"   # 🔥
        PARTY = "5046509860389126442"  # 🎉
        HEART = "5159385139981059251"  # ❤️
        THUMBS_UP = "5107584321108051014"  # 👍
        THUMBS_DOWN = "5104858069142078462"  # 👎
        POOP = "5046589136895476101"  # 💩

        def __str__(self) -> str:
            return self.value

    def set_message_effect_id(self, effect: str):
        self.message_effect_id = effect

    def set_effect(self, effect: Effect | str | int):
        self.message_effect_id = str(effect)

    def set_photo(self, photo: str | None | Any):
        self.media = []
        if not isinstance(photo, str):
            self.photo = photo
            return 

        if photo.startswith(("http://", "https://")):
            self.photo = photo
            return
        
        with open(photo, "rb") as photo:
            self.photo = photo.read()

    def set_media(self, *media: str | Any):
        """Sets the photos to be sent as InputMediaPhoto objects."""
        self.photo = None
        self.media: list[InputMediaPhoto] = []

        for m in media:
            if isinstance(m, InputMediaPhoto):
                self.media.append(m)
                continue

            if not isinstance(m, str):
                # assume it's a file-like object or bytes
                self.media.append(InputMediaPhoto(media=m))
                continue

            if m.startswith(("http://", "https://")):
                self.media.append(InputMediaPhoto(media=m))
                continue

            # assume it's a local file path
            self.media.append(InputMediaPhoto(media=InputFile(open(m, "rb"))))

    def _prepare_media(self):
        if self.media:
            def f(media: InputMediaPhoto):
                media.parse_mode = self.parse_mode
                return media
            self.media[0].caption = self.text
            self.media = list(map(f, self.media))

    def set_chat_id(self, chat_id: int):
        self.chat_id = chat_id

    def set_text(self, text: str):
        self.text = text

    def set_reply_markup(self, reply_markup):
        self.reply_markup = reply_markup

    def set_temporary(self, is_temp: bool):
        self.is_temporary = is_temp

    def set_delete_temporaries(self, del_temps: bool):
        self.delele_temporaries = del_temps

    def set_parse_mode(self, parse_mode: str | None):
        if not parse_mode:
            self.parse_mode = None
            return
        
        if parse_mode.lower() in ("html", "markdown"):
            self.parse_mode = parse_mode.lower()
            self.styles.set_parse_mode(self.parse_mode)

    def set_reply_to_message_id(self, reply_to_message_id: int | None):
        self.reply_to_message_id = reply_to_message_id

    def set_edit_message_id(self, edit_message_id: int | None):
        self.edit_message_id = edit_message_id

    def set_edit_message(self, edit_message: Message | None):
        if getattr(edit_message, "message_id", None) is not None:
            self.edit_message_id = edit_message.message_id # type: ignore

    def set_reply_to(self, reply_to: Message | None):
        if getattr(reply_to, "message_id", None) is not None:
            self.reply_to_message_id = reply_to.message_id # type: ignore

    def _get_send_configs(self) -> dict[str, Any]:
        return {
            "chat_id": self.chat_id,
            "parse_mode": self.parse_mode,
            "message_thread_id": self.thread_id,
            "reply_to_message_id": self.reply_to_message_id,
        }

    def _get_send_args(self) -> dict[str, Any]:
        args: dict[str, Any] = {
            "reply_markup": self.reply_markup,
        }

        if self.message_effect_id:
            args["message_effect_id"] = self.message_effect_id

        args.update(self._get_send_configs())

        return args

    def _get_edit_configs(self) -> dict[str, Any]:
        return {
            "chat_id": self.chat_id,
            # "message_thread_id": self.thread_id,
            "message_id": self.edit_message_id,
        }
    
    def _add_temporary(self, message_id: int):
        TemporaryMsgStore.add_temporary(self.chat_id, message_id)

    def _remove_temporary(self):
        TemporaryMsgStore.remove_temporary(self.bot, self.chat_id)

    def _handle_is_temp(self, message: Message | None):
        if self.is_temporary and message:
            self._add_temporary(message.message_id)

    def _handle_del_temps(self):
        if self.delele_temporaries:
            self._remove_temporary()

    def _handle_temporary(self, message: Message | None, edited: bool=False):
        if not edited:
            self._handle_del_temps()
        
        self._handle_is_temp(message)

    def _send(self) -> Message | None:
        if self.photo:
            return self._send_photo()
        elif self.media:
            return self._send_media()
        else:
            return self._send_text()
        
    def _send_photo(self) -> Message | None:
        return self.bot.send_photo(
            photo=self.photo,
            caption=self.text,
            **self._get_send_args()
        )
    
    def _send_media(self) -> Message | None:
        self._prepare_media()
        media: list[InputMediaAudio | InputMediaDocument | InputMediaPhoto | InputMediaVideo] = list(self.media)

        return self.bot.send_media_group(
            media=media,
            reply_to_message_id=self.reply_to_message_id,
            chat_id=self.chat_id
        )[0]

    def _send_text(self) -> Message | None:
        return self.bot.send_message(
            text=self.text,
            **self._get_send_args()
        )

    def _edit(self) -> Message | None: # type: ignore
        configs = self._get_edit_configs()

        if not self.edit_message_id:
            raise ValueError("edit_message_id is None: Unable to edit message without a valid message ID.")

        if self.photo:
            media = InputMediaPhoto(
                media=self.photo, 
                caption=self.text, 
                parse_mode=self.parse_mode
            )
            message = self.bot.edit_message_media(
                media=media,
                reply_markup=self.reply_markup,  # type: ignore
                **configs
            )
        else:
            message = self.bot.edit_message_text(
                text=self.text,
                parse_mode=self.parse_mode,
                reply_markup=self.reply_markup,  # type: ignore
                **configs
            )

        if isinstance(message, Message):
            return message

    def _edit_or_send(self) -> tuple[Message | None, bool]:
        if self.edit_message_id:

            try:
                return self._edit(), True
            except Exception as exception:
                self._delete_message(self.edit_message_id)
                library.warning(f"Failed to edit message {self.edit_message_id}, sending new one instead. Exception: {exception}")
        
        return self._send(), False
    
    def _delete_message(self, message_id: int | None) -> bool:
        """
        Deletes a message by its ID.

        Args:
            message_id (int): The ID of the message to delete.
        """
        if message_id is None:
            return False
        
        try:
            return self.bot.delete_message(chat_id=self.chat_id, message_id=message_id)
        except Exception as exception:
            library.warning(f"Failed to delete message {message_id}. Maybe the user deleted it. Exception: {exception}")
            return False
        
    def delete_message(self, message: Message | None, only_user_messages: bool=False) -> bool:
        if only_user_messages and message and message.from_user and message.from_user.is_bot:
            return False

        return self._delete_message(self.get_message_id(message))

    def pyerror(self, exception: BaseException) -> Message | None: # type: ignore
        """
        Sends a message with the Python exception details for debugging.

        Args:
            exception (BaseException): The exception that occurred.

        Returns:
            Message | None: The error message sent or None if sending failed.
        """
        try:
            configs = self._get_send_configs()
            configs["parse_mode"] = "HTML"
            return self.bot.send_message(text=f"<b>{type(exception).__name__}</b>\n\n<i>{exception}.</i>", **configs)
        except Exception as exception:
            library.warning(f"Failed to send `pyerror` message: {exception}")
            return None

    def error(self, title: str | StyleFormatter, message: str | StyleFormatter) -> Message | None: # type: ignore
        """
        Sends a custom error message with a title and detailed message.

        Args:
            title (str): The title of the error.
            message (str): The error message.

        Returns:
            Message | None: The sent error message or None if sending failed.
        """
        try:
            configs = self._get_send_configs()
            configs["parse_mode"] = "HTML"
            return self.bot.send_message(text=f"<b>{title}</b>\n\n<i>{message}.</i>", **configs)
        except Exception as exception:
            library.warning(f"Failed to send `error` message: {exception}")
            return None
    
    def try_send(self) -> tuple[Message | None, Exception | None]:
        """
        Attempts to send a message, handling potential exceptions.

        Returns:
            tuple[Message | None, Exception | None]: 
                A tuple containing the sent message (or None if an error occurred) 
                and the exception (if any).
        """
        try:
            return self.send(), None
        except Exception as exception:
            library.warning(f"Failed to send message in `try_send`: {exception}")
            return None, exception

    def send_or_handle_error(self) -> Message | None:
        """
        Attempts to send a message and handles any errors that occur.

        This method tries to send a message using the `try_send()` function. If an error occurs
        during sending, it sends a message with the error details using `pyerror()`. 

        Returns:
            Message | None: The sent message if successful, or None if an error occurred and was handled.
        """
        message, error = self.try_send()
    
        if error:
            self.pyerror(error)
        
        return message
        
    def send(self) -> Message | None:
        """
        Sends or edits a message and handles its temporary status.

        Returns:
            Message | None: The sent or edited message.
        """
        message, edited = self._edit_or_send()

        self._handle_temporary(message, edited)

        return message

    def get_message_id(self, message: Message | None) -> int | None: # type: ignore
        """
        Retrieves the message ID from a Message object.

        Args:
            message (Message): The message object.

        Returns:
            int | None: The message ID or None if the message is invalid (None).
        """
        if message:
            return message.message_id
        
# ---------------------------------------------------------------------------------
# Alert Sender
# ---------------------------------------------------------------------------------
    
from enum import Enum, unique

@unique
class ParseMode(Enum):
    HTML = "html"
    MARKDOWN = "markdown"
    NONE = None

class AlertSender(BaseSender):

    _title: str | StyleFormatter
    _message: str | StyleFormatter | tuple[str | StyleFormatter, ...]
    _text: str | StyleFormatter
    _parse_mode: ParseMode | None

    _use_italics: bool
    _use_newline: bool

    def _compile_text(self) -> None:
        if not hasattr(self, "_title"):
            self._title = ""

        if not hasattr(self, "_message"):
            self._message = ""

        if not hasattr(self, "_parse_mode"):
            self._parse_mode = None

        if not hasattr(self, "_use_newline"):
            self._use_newline = True
        
        if not hasattr(self, "_use_italics"):
            self._use_italics = True

        if not hasattr(self, "_text"):
            self._text = ""

        if self._text:
            self._compile_plain()
        elif self._title or self._message:
            self._compile_alert()

    def _compile_plain(self):
        if self._parse_mode:
            super().set_parse_mode(self._parse_mode.value)

        if isinstance(self._text, StyleFormatter):
            self._text.set_parse_mode(self.parse_mode)

        super().set_text(str(self._text))

    def _compile_alert(self):
        if self._parse_mode:
            super().set_parse_mode(self._parse_mode.value)
        else:
            super().set_parse_mode("html")

        title = self.styles.bold(NoSanitize(self._title)) if self._title else None

        if self._message:
            if isinstance(self._message, (str, StyleFormatter)):
                parts = (self._message, )
            else:
                parts = self._message

            message = NoSanitize(*parts)

            if self._use_italics:
                message = self.styles.italic(message)
        else:
            message = None

        text_parts = []

        if title:
            text_parts.append(title)
        
        if title and message and self._use_newline:
            text_parts.append("\n\n")

        if message:
            text_parts.append(message)

        text = Composite(*text_parts)
        text.set_parse_mode(self.parse_mode)

        super().set_text(str(text))

    def set_text(self, text: str | StyleFormatter):
        self._text = text
        self._title = ""
        self._message = ""

    def set_title(self, title: str | StyleFormatter):
        self._text = ""
        self._title = title

    def set_message(self, *message: str | StyleFormatter, sep: str | StyleFormatter=""):
        self._text = ""
        self._message = self._interleave(message, sep)

    def add_message(self, *message: str | StyleFormatter, sep: str | StyleFormatter=""):
        self._text = ""

        previous = self._message
        
        if not isinstance(previous, tuple):
            if previous:
                previous = (previous, )
            else:
                previous = tuple()

        self._message = previous + self._interleave(message, sep)

    def set_parse_mode(self, parse_mode: str | None=None):
        try:
            if parse_mode:
                self._parse_mode = ParseMode(parse_mode.lower())
            else:
                self._parse_mode = ParseMode(None)
        except ValueError:
            raise ValueError(f"Unknown parse_mode: {parse_mode}")

    def set_use_italics(self, use_italics: bool=True):
        self._use_italics = use_italics

    def set_use_newline(self, use_newline: bool=True):
        self._use_newline = use_newline

    def send(self) -> Message | None:
        self._compile_text()
        return super().send()

    def _interleave(self, message: tuple, sep):
        if not sep:
            return message
        if not message:
            return tuple()
        if len(message) == 1:
            return message
        
        result = [item for pair in zip(message, [sep]*(len(message)-1)) for item in pair] + [message[-1]]
        return tuple(result)