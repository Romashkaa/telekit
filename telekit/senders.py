# Copyright (c) 2025 Ving Studio, Romashka
# Licensed under the MIT License. See LICENSE file for full terms.

from typing import Any
from enum import Enum
import io

from telebot import TeleBot
from telebot.types import (
    Message, InputMediaPhoto, InputFile, InputMediaAudio, InputMediaDocument, InputMediaVideo
)

from telekit.styles import NoSanitize, StyleFormatter, Composite, Styles
from .logger import logger
library = logger.library

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

    def __init__(
            self,
            chat_id: int,

            text: str = "",
            reply_markup = None,

            is_temporary: bool = False,
            delele_temporaries: bool = True,
            
            parse_mode: str | None = None,
            reply_to_message_id: int | None = None,

            edit_message_id: int | None = None,

            thread_id: int | None = None,
            effect_id: str | None = None,

            photo: str | None = None,
            document: str | Any = None,
            video_note: str | Any = None,  
            animation: str | Any = None,
            video: str | Any = None,
            audio: str | Any = None,
            voice: str | Any = None,
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
        self.document = document
        self.video = video
        self.animation = animation
        self.audio = audio
        self.voice = voice  
        self.video_note = video_note

        self.venue = []

        self.styles = Styles()

        self.media = []

        if self.parse_mode:
            self.styles.set_parse_mode(self.parse_mode)

    # --------------------------------------------------------
    # Enums for message effects and chat actions
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Setter methods for configuring media attachments
    # --------------------------------------------------------

    def remove_attachments(self):
        """
        Clear all attachments from the sender:
        - `photo`
        - `document`
        - `animation`
        - `video_note`
        - `video`
        - `audio`
        - `voice`
        - `media`
        - `venue`
        """
        self.media: list[InputMediaPhoto] = []
        self.video_note: str | Any = None
        self.animation: str | Any = None
        self.document: str | Any = None
        self.photo: str | Any = None
        self.video: str | Any = None
        self.audio: str | Any = None
        self.voice: str | Any = None
        self.venue: list[Any] = []

    def set_photo(self, photo: str | None | Any):
        """
        Sets the photo for the message.
         
        Accepts:
            - URL string (`"http://..."` or `"https://..."`)
            - local file path
            - bytes or file-like object
            - `None` to remove any previously set photo
        
        :param photo: The photo for the message
        :type photo: str | None | Any
        """
        if photo is None:
            self.photo = None
            return

        self.remove_attachments()
        self.photo = self._load_item(photo)

    def set_document(self, document: str | None | Any):
        """
        Sets the document for the message.
         
        Accepts:
            - URL string (`"http://..."` or `"https://..."`)
            - local file path
            - bytes or file-like object
            - `None` to remove any previously set document
        
        :param document: File to send.
        :type document: str | None | Any
        """
        if document is None:
            self.document = None
            return

        self.remove_attachments()
        self.document = self._load_item(document)

    def set_text_as_document(self, text: str | None, name: str="text.txt", encoding: str="utf-8"):
        """
        Set a text string as a document to be sent.

        This method converts the given text into an in-memory file-like object (`BytesIO`) 
        and sets it as a document. The provided `name` is only a **placeholder filename** 
        for Telegram; no actual file is created on disk.
            
        :param text: The text content to convert into a document. If None, removes any previously set document.
        :type text: str | None
        :param name: The placeholder filename for the document (default "text.txt").
        :type name: str
        :param encoding: The text encoding used to convert the string to bytes (default "utf-8").
        :type encoding: str
        """
        if text is None:
            self.set_document(None)
            return
        
        document = io.BytesIO(text.encode(encoding))
        document.name = name

        self.set_document(document)

    def set_video(self, video: str | None | Any):
        """
        Sets the video for the message.
         
        Accepts:
            - URL string (`"http://..."` or `"https://..."`)
            - local file path
            - bytes or file-like object
            - `None` to remove any previously set video
        
        :param video: The video for the message
        :type video: str | None | Any
        """
        if video is None:
            self.video = None
            return

        self.remove_attachments()
        self.video = self._load_item(video)

    def set_animation(self, animation: str | None | Any):
        """
        Sets the animation for the message.
         
        Accepts:
            - URL string (`"http://..."` or `"https://..."`)
            - local file path
            - bytes or file-like object
            - `None` to remove any previously set animation
        
        :param animation: The animation for the message
        :type animation: str | None | Any
        """
        if animation is None:
            self.animation = None
            return

        self.remove_attachments()
        self.animation = self._load_item(animation)

    def set_audio(self, audio: str | None | Any):
        """
        Sets the audio for the message.
         
        Accepts:
            - URL string (`"http://..."` or `"https://..."`)
            - local file path
            - bytes or file-like object
            - `None` to remove any previously set audio
        
        :param audio: The audio for the message
        :type audio: str | None | Any
        """
        if audio is None:
            self.audio = None
            return

        self.remove_attachments()
        self.audio = self._load_item(audio)

    def set_voice(self, voice: str | None | Any):
        """
        Sets the voice for the message.
         
        Accepts:
            - URL string (`"http://..."` or `"https://..."`)
            - local file path
            - bytes or file-like object
            - `None` to remove any previously set voice
        
        :param voice: The voice for the message
        :type voice: str | None | Any
        """
        if voice is None:
            self.voice = None
            return

        self.remove_attachments()
        self.voice = self._load_item(voice)

    def set_video_note(self, video_note: str | None | Any):
        """
        Sets the video note for the message.
         
        Accepts:
            - local file path
            - bytes or file-like object
            - `None` to remove any previously set video note
            
        Sending video notes by a URL is currently unsupported.
        
        :param video_note: The video note for the message
        :type video_note: str | None | Any

        """
        if video_note is None:
            self.video_note = None
            return

        self.remove_attachments()
        video_note = self._load_item(video_note)

        if isinstance(video_note, str) and video_note.startswith(("http://", "https://")):
            raise ValueError("Sending video notes by a URL is currently unsupported")

        self.video_note = video_note

    def set_venue(
            self, 
            latitude: float | None, 
            longitude: float | None, 
            title: str,
            address: str,
            foursquare_id: str | None = None,
            foursquare_type: str | None = None,
        ):
        """
        Sets the venue for the message.
        """
        self.bot.send_venue
        
        self.remove_attachments()
        self.venue = [
            latitude, longitude, 
            address, title,
            foursquare_id, foursquare_type
        ]

    def _load_item(self, item: str | Any):
        if not isinstance(item, str):
            return item

        if item.startswith(("http://", "https://")):
            return item
        
        with open(item, "rb") as item:
            return item.read()

    def set_media(self, *media: str | Any):
        """
        Sets the photos to be sent as InputMediaPhoto objects.
        
        Accepts:
            - URLs
            - local file paths
            - bytes or file-like objects
            - instances of `InputMediaPhoto`
        """
        if not media:
            self.media: list[InputMediaPhoto] = []
            return

        self.remove_attachments()

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

    # --------------------------------------------------------
    # Setter methods for configuring message properties
    # --------------------------------------------------------

    def set_message_effect_id(self, effect: str):
        """
        Sets the message effect by string ID. Low-level version of the `set_effect` method
        
        :param effect: Effect ID
        :type effect: str
        """
        self.message_effect_id = effect

    def set_effect(self, effect: Effect | str | int):
        """
        Sets a message effect using enum, string, or integer.
        
        :param effect: Integer, String, or Enum representing the message effect
        :type effect: Effect | str | int
        """
        self.message_effect_id = str(effect)

    def set_chat_id(self, chat_id: int):
        """
        Sets the chat ID for sending messages
        
        :param chat_id: The telegram chat ID
        :type chat_id: int
        """
        self.chat_id = chat_id

    def set_text(self, text: str):
        """
        Sets the plain text of the message.
        
        :param text: A simple text message. Not sanitized. HTML and Markdown tags are allowed
        :type text: str
        """
        self.text = text

    def set_reply_markup(self, reply_markup):
        """
        Sets Inline keyboards, reply keyboards, or other markup objects
        """
        self.reply_markup = reply_markup

    def set_temporary(self, is_temp: bool):
        """
        Marks message as temporary; will be deleted later if `delete_temporaries` is True.  
        """
        self.is_temporary = is_temp

    def set_delete_temporaries(self, del_temps: bool):
        """
        Whether to delete temporary messages in the chat.  
        """
        self.delele_temporaries = del_temps

    def set_parse_mode(self, parse_mode: str | None):
        """
        Sets the parse mode to the message
        
        :param parse_mode: `html`, `markdown` or `None`.  
        :type parse_mode: str | None
        """
        if not parse_mode:
            self.parse_mode = None
            return
        
        if parse_mode.lower() in ("html", "markdown"):
            self.parse_mode = parse_mode.lower()
            self.styles.set_parse_mode(self.parse_mode)

    def set_reply_to_message_id(self, reply_to_message_id: int | None):
        """
        Reply to specific message by ID.
        """
        self.reply_to_message_id = reply_to_message_id

    def set_edit_message_id(self, edit_message_id: int | None):
        """
        Edit an existing message by ID.
        """
        self.edit_message_id = edit_message_id

    def set_edit_message(self, edit_message: Message | None):
        """
        Edit a specific message by its `Message` object.  
        """
        if edit_message is None:
            self.edit_message_id = None
            return

        if getattr(edit_message, "message_id", None) is not None:
            self.edit_message_id = edit_message.message_id

    def set_reply_to(self, reply_to: Message | None):
        """
        Reply to a specific message by its `Message` object.  
        """
        if reply_to is None:
            self.reply_to = None
            return

        if getattr(reply_to, "message_id", None) is not None:
            self.reply_to_message_id = reply_to.message_id

    # --------------------------------------------------------
    # Methods for preparing send and edit message configurations
    # --------------------------------------------------------

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
    
    # --------------------------------------------------------
    # Internal methods for managing temporary messages
    # --------------------------------------------------------
    
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

    # --------------------------------------------------------
    # Internal send dispatcher
    # --------------------------------------------------------

    def _send(self) -> Message | None:
        if self.photo:
            return self._send_photo()
        elif self.document:
            return self._send_document()
        elif self.video:
            return self._send_video()
        elif self.animation:
            return self._send_animation()
        elif self.audio:
            return self._send_audio()
        elif self.voice:
            return self._send_voice()
        elif self.video_note:
            return self._send_video_note()
        elif self.venue:
            return self._send_venue()
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
    
    def _send_document(self) -> Message | None:
        return self.bot.send_document(
            document=self.document,
            caption=self.text,
            **self._get_send_args()
        )
    
    def _send_video(self) -> Message | None:
        return self.bot.send_video(
            video=self.video,
            caption=self.text,
            **self._get_send_args()
        )
    
    def _send_animation(self) -> Message | None:
        return self.bot.send_animation(
            animation=self.animation,
            caption=self.text,
            **self._get_send_args()
        )
    
    def _send_audio(self) -> Message | None:
        return self.bot.send_audio(
            audio=self.audio,
            caption=self.text,
            **self._get_send_args()
        )
    
    def _send_voice(self) -> Message | None:
        return self.bot.send_voice(
            voice=self.voice,
            caption=self.text,
            **self._get_send_args()
        )
    
    def _send_video_note(self) -> Message | None:
        return self.bot.send_video_note(
            data=self.video_note,
            chat_id=self.chat_id,
            reply_to_message_id=self.reply_to_message_id,
            reply_markup=self.reply_markup,
            message_effect_id=self.message_effect_id
        )
    
    def _send_venue(self) -> Message | None:
        return self.bot.send_venue(
            latitude=self.venue[0],
            longitude=self.venue[1],
            title=self.venue[2],
            address=self.venue[3],
            foursquare_id=self.venue[4],
            foursquare_type=self.venue[5],
            chat_id=self.chat_id,
            reply_to_message_id=self.reply_to_message_id,
            reply_markup=self.reply_markup,
            message_effect_id=self.message_effect_id
        )
    
    def _send_media(self) -> Message | None:
        self._prepare_media()
        media: list[InputMediaAudio | InputMediaDocument | InputMediaPhoto | InputMediaVideo] = list(self.media)

        return self.bot.send_media_group(
            media=media,
            reply_to_message_id=self.reply_to_message_id,
            chat_id=self.chat_id
        )[0]
    
    # --------------------------------------------------------
    # Internal methods for sending and editing messages
    # --------------------------------------------------------

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
    
    # --------------------------------------------------------
    # Metods for deleting messages
    # --------------------------------------------------------
    
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
        """
        Deletes a message optionally ignoring bot messages.  
        """
        if only_user_messages and message and message.from_user and message.from_user.is_bot:
            return False

        return self._delete_message(self.get_message_id(message))
    
    # --------------------------------------------------------
    # Methods for sending and editing messages 
    # --------------------------------------------------------

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
    
    # --------------------------------------------------------
    # Methods for sending chat actions and retrieving message IDs
    # --------------------------------------------------------
    
    def send_chat_action(self, action: str | ChatAction, timeout: int | None = None):
        """
        Send a chat action to a chat.

        ```
        self.chain.sender.send_chat_action(self.chain.sender.ChatAction.UPLOAD_AUDIO)
        self.chain.sender.send_chat_action("upload_audio")
        ```
        
        :param action: Type of action to broadcast. Choose one, depending on what the user is about to receive: typing for text messages, upload_photo for photos, record_video or upload_video for videos, record_voice or upload_voice for voice notes, upload_document for general files, choose_sticker for stickers, find_location for location data, record_video_note or upload_video_note for video notes.
        :type action: str | ChatAction
        :param timeout: Timeout in seconds for the request.
        :type timeout: int | None
        """
        self.bot.send_chat_action(self.chat_id, str(action), timeout)

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
        
    # --------------------------------------------------------
    # Context manager support methods
    # --------------------------------------------------------
        
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False
    
    def then_send(self):
        """
        Returns a context manager that yields the sender instance. 

        When exiting the context block, the message will be automatically sent.
        
        Example usage:
        
        with self.chain.sender.then_send() as sender:
            sender.set_title("Hello!")
            sender.set_message("It's Telekit.")
        # At the end of the block, send() is called automatically.
        """
        class AutoSendContext:
            def __init__(self, sender: BaseSender):
                self.sender = sender

            def __enter__(self):
                return self.sender

            def __exit__(self, exc_type, exc_val, exc_tb):
                self.sender.send()
                return False

        return AutoSendContext(self)
        
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
    _additional: tuple[StyleFormatter | str, ...]

    _use_italics: bool
    _use_newline: bool

    # --------------------------------------------------------
    # Internal methods for compiling and formatting message text
    # --------------------------------------------------------

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

        if not hasattr(self, "_additional"):
            self._additional = tuple()

        if self._text:
            self._compile_plain()
        elif self._title or self._message:
            self._compile_alert()

    def _compile_plain(self):
        if self._parse_mode:
            super().set_parse_mode(self._parse_mode.value)

        if isinstance(self._text, StyleFormatter):
            self._text.set_parse_mode(self.parse_mode)

        if self._additional:
            self._text = NoSanitize(self._text, *self._additional)

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

            if self._additional:
                message = NoSanitize(message, *self._additional)

            if self._use_italics:
                message = self.styles.italic(message)
        elif self._additional:
            if self._use_italics:
                message = self.styles.italic(NoSanitize(*self._additional))
            else:
                message = NoSanitize(*self._additional)
        else:
            message = None

        text_parts = []

        if title:
            text_parts.append(title)
        
        if self._use_newline and title and message:
            text_parts.append("\n\n")

        if message:
            text_parts.append(message)

        text = Composite(*text_parts)
        text.set_parse_mode(self.parse_mode)

        super().set_text(str(text))

    def _interleave(self, message: tuple, sep):
        if not sep:
            return message
        if not message:
            return tuple()
        if len(message) == 1:
            return message
        
        result = [item for pair in zip(message, [sep]*(len(message)-1)) for item in pair] + [message[-1]]
        return tuple(result)

    # --------------------------------------------------------
    # Setter methods for configuring alert-styled message properties
    # --------------------------------------------------------

    def set_text(self, *text: str | StyleFormatter, sep: str | StyleFormatter=""): # pyright: ignore[reportIncompatibleMethodOverride]
        """
        Set a plain text message, replacing any previously set title or message.

        Args:
            *text: One or more text parts or StyleFormatter objects to set. Not sanitized. HTML and Markdown tags are allowed
            sep (str | StyleFormatter, optional): Separator used between text parts. Defaults to "".

        Returns:
            None

        Example:
        ```
        s.set_text("Hello", Bold("World"), sep=" ")
        # Result: "Hello <b>World</b>"
        ```
        """
        self._text = NoSanitize(*self._interleave(text, sep))
        self._title = ""
        self._message = ""
        self._additional = tuple()

    def set_title(self, title: str | StyleFormatter):
        """
        Set the title of the alert message. Clears plain text content.

        Args:
            title (str | StyleFormatter): Title of the alert-styled message. Not sanitized. HTML and Markdown tags are allowed

        Returns:
            None
        """
        self._text = ""
        self._title = title
        self._additional = tuple()

    def set_message(self, *message: str | StyleFormatter, sep: str | StyleFormatter=""):
        """
        Set the main message body for the alert.

        Args:
            *message: One or more message parts or StyleFormatter objects. Not sanitized. HTML and Markdown tags are allowed
            sep (str | StyleFormatter, optional): Separator used between message parts. Defaults to "".

        Returns:
            None
        """
        self._text = ""
        self._message = self._interleave(message, sep)
        self._additional = tuple()

    def add_message(self, *message: str | StyleFormatter, sep: str | StyleFormatter=""):
        """
        Appends text to the end of the current message.

        This method does not replace the existing content.
        Instead, it adds the provided text after the current message,
        preserving everything that was already set.

        Works the same way for both `set_text()` and `set_message()`.

        Not sanitized. HTML and Markdown tags are allowed

        Example:
        ```
            s.set_text("Hel")
            s.append("lo") # add_message == append

            # Result:
            # "Hello"
        ```
        """
        if hasattr(self, "_additional"):
            previous = self._additional
        else:
            previous = None
        
        if not isinstance(previous, tuple):
            previous = tuple()

        self._additional = previous + self._interleave(message, sep)

    append = add_message

    def set_parse_mode(self, parse_mode: str | None=None):
        """
        Set the parse mode for message rendering.

        Args:
            parse_mode (str | None): Parse mode as 'html', 'markdown', or None.

        Raises:
            ValueError: If parse_mode is not recognized.

        Returns:
            None
        """
        try:
            if parse_mode:
                self._parse_mode = ParseMode(parse_mode.lower())
            else:
                self._parse_mode = ParseMode(None)
        except ValueError:
            raise ValueError(f"Unknown parse_mode: {parse_mode}")

    def set_use_italics(self, use_italics: bool=True):
        """
        Enable or disable italics for message body.

        Args:
            use_italics (bool): True to enable italics, False to disable.

        Returns:
            None
        """
        self._use_italics = use_italics

    def set_use_newline(self, use_newline: bool=True):
        """
        Enable or disable automatic newline between title and message body.

        Args:
            use_newline (bool): True to insert newline, False to omit.

        Returns:
            None
        """
        self._use_newline = use_newline

    # --------------------------------------------------------
    # Method to compile and send the message
    # --------------------------------------------------------

    def send(self) -> Message | None:
        """
        Compile and send the current message.

        Resolves internal state into final text before sending through
        BaseSender's send method.

        Note:
            This method only sends the message itself. It does not handle inline
            keyboard interactions, so button presses will not be registered unless
            they are links. To properly send a message that supports inline buttons,
            use `chain.send()`.

        Returns:
            Message | None: The sent message object or None if sending failed.
        """
        self._compile_text()
        return super().send()