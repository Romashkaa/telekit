from typing import Any
from enum import Enum
from telebot import TeleBot # type: ignore
from telebot.types import ( # type: ignore
    Message, InputMediaPhoto
)

class TempBuffer:

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
    
class PagesBuffer:

    _last_pages: dict[int, str] = {}
    _pages: dict[int, str] = {}

    @classmethod
    def set_page(cls, chat_id: int, page: str):
        cls._last_pages[chat_id] = cls._pages.get(chat_id, "")
        cls._pages[chat_id] = page

    @classmethod
    def get_page(cls, chat_id: int) -> str:
        return cls._pages.get(chat_id, "")

    @classmethod
    def get_last_page(cls, chat_id: int) -> str:
        return cls._last_pages.get(chat_id, "")
    
    @classmethod
    def debug(cls, chat_id: int | None=None) -> dict[str, int]:
        return {
            "pb.all_pages": len(cls._pages),
            "pb.user_pages": len(cls._pages.get(chat_id, "")), # type: ignore

            "pb.all_last_pages": len(cls._last_pages),
            "pb.user_last_pages": len(cls._last_pages.get(chat_id, "")) # type: ignore
        }
        

class BaseSender:

    bot: TeleBot

    @classmethod
    def init(cls, bot: TeleBot):
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
                 
                 parse_mode: str | None = "HTML",
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

    class Effect(Enum):
        FIRE = "5104841245755180586"   # 🔥
        THUMBS_UP = "5107584321108051014"  # 👍
        HEART = "5159385139981059251"  # ❤️
        PARTY = "5046509860389126442"  # 🎉
        THUMBS_DOWN = "5104858069142078462"  # 👎
        POOP = "5046589136895476101"  # 💩

        def __str__(self) -> str:
            return self.value

    def set_message_effect_id(self, effect: str):
        self.message_effect_id = effect

    def set_effect(self, effect: Effect | str | int):
        self.message_effect_id = str(effect)

    def set_photo(self, photo: str | None):
        self.photo = photo

    def set_chat_id(self, chat_id: int):
        self.chat_id = chat_id

    def set_text(self, text: str):
        self.text = text

    def set_reply_markup(self, reply_markup): # type: ignore
        self.reply_markup = reply_markup # type: ignore

    def set_temporary(self, is_temp: bool):
        self.is_temporary = is_temp

    def set_delete_temporaries(self, del_temps: bool):
        self.delele_temporaries = del_temps

    def set_parse_mode(self, parse_mode: str | None):
        if not parse_mode:
            return
        
        if parse_mode.lower() in ("html", "markdown"):
            self.parse_mode = parse_mode.lower()

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
            # "caption" if self.photo else "text": self.text,
            "reply_markup": self.reply_markup, # type: ignore
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
        TempBuffer.add_temporary(self.chat_id, message_id)

    def _remove_temporary(self):
        TempBuffer.remove_temporary(self.bot, self.chat_id)

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
        else:
            return self._send_text()
        
    def _send_photo(self) -> Message | None:
        return self.bot.send_photo(
            photo=self.photo,
            caption=self.text,
            **self._get_send_args()
        )

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
            except:
                self._delete_message(self.edit_message_id)
                # print(f"Error editing message: {e}, sending new message instead.")
        
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
        except:
            # print(f"Error deleting message {message_id}: {e}")
            return False
        
    def delete_message(self, message: Message | None) -> bool:
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
        except Exception:
            pass

    def error(self, title: str, message: str) -> Message | None: # type: ignore
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
        except Exception:
            pass
    
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


class TextSender(BaseSender):
    pass
    

class AlertSender(BaseSender):

    _title: str
    _message: str

    _use_italics: bool
    _add_new_line: bool

    def _compile_text(self, use_italics: bool=True) -> None:

        if self.parse_mode == "markdown":
            _start_bold = "*"
            _end_bold = "*"
            _start_italic = "_"
            _end_italic = "_"
        else:
            _start_bold = "<b>"
            _end_bold = "</b>"
            _start_italic = "<i>"
            _end_italic = "</i>"

        if not hasattr(self, "_title"):
            self._title = ""

        if not hasattr(self, "_message"):
            self._message = ""

        if self.text and not (self._message or self._title):
            return
        
        if self._message and not self._title:
            self.set_text(self._message)
            return

        new_line: str = "\n\n" if getattr(self, "_add_new_line", True) else ""

        if getattr(self, "_use_italics", True):
            text = f"{_start_bold}{self._title}{_end_bold} {new_line}{_start_italic}{self._message}{_end_italic}"
        else:
            text = f"{_start_bold}{self._title}{_end_bold} {new_line}{self._message}"

        self.set_text(text)

    def set_title(self, title: str):
        self._title = title

    def set_message(self, *message: str, sep: str=""):
        self._message = sep.join(message)

    def set_use_italics(self, use_italics: bool=True):
        self._use_italics = use_italics

    def set_add_new_line(self, _add_new_line: bool=True):
        self._add_new_line = _add_new_line

    def send(self) -> Message | None:
        self._compile_text()
        return super().send()
