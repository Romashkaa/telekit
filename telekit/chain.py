import random
from typing import Callable, Any

import telebot              # type: ignore
from telebot.types import ( # type: ignore
    Message, 
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from . import senders
from . import input_handler
from . import timeout

import charset_normalizer
from dataclasses import dataclass

__all__ = ["TextDocument", "Chain"]

@dataclass
class TextDocument:
    message: telebot.types.Message
    document: telebot.types.Document
    file_name: str
    encoding: str
    text: str

class Chain:

    bot: telebot.TeleBot
    
    @classmethod
    def init(cls, bot: telebot.TeleBot):
        """
        Initializes the bot instance for the class.

        Args:
            bot (TeleBot): The Telegram bot instance to be used for sending messages.
        """
        cls.bot = bot
        
    def __init__(self, chat_id: int):
        self.chat_id = chat_id
        self.sender = senders.AlertSender(chat_id)
        self.handler = input_handler.InputHandler(chat_id)
        self.parent: Chain | None = None
        self._previous_message: Message | None = None
        self.always_edit_previous_message: bool = False
        
        self._timeout_handler = timeout.TimeoutHandler()

    def set_inline_keyboard(self, keyboard: dict[str, 'Chain' | Callable[..., Any] | str], row_width: int = 1) -> None:
        """
        Sets an inline keyboard for the chain, where each button triggers the corresponding action.
        Every button calls its associated function with the message as an argument (if applicable).
        
        ---
        ### Example 1 (callback types):
        ```
        self.chain.set_inline_keyboard(
            {   
                # When the user clicks this button, `prompt.send()` will be executed
                "« Change": prompt,
                # When the user clicks this button, this lambda function will run
                "Yes »": lambda: print("User: Okay!"),
                # Can even be a link
                "Youtube": "https://youtube.com"
            }, row_width=2
        )
        ```

        ### Example 2 (methods):
        ```
        self.chain.set_inline_keyboard(
            {   
                "« Change": self.entry_name,
                "Next »": self.entry_age,
            }, row_width=2
        )
        ```
        ---
        ## Callable types:
        `Callable[..., Any]` may be:
            - `Callable[[Message], Any]` — accepts a Message object, or 
            - `Callable[[], Any]` — takes no arguments.
        ---
        Args:
            keyboard (dict[str, Callable[[Message], Any] | str]): A dictionary where keys are button captions
                and values are functions to be called when the button is clicked.
        """
        callback_functions: dict[str, Callable[[Message], Any]] = {}
        buttons: list[InlineKeyboardButton] = []

        for i, (caption, callback) in enumerate(keyboard.items()):
            if isinstance(callback, str):
                buttons.append(
                    InlineKeyboardButton(
                        text=caption,
                        url=callback
                    )
                )
            else:
                callback_data = f"button_{i}_{random.randint(1000, 9999)}"
                callback_functions[callback_data] = callback
                buttons.append(
                    InlineKeyboardButton(
                        text=caption,
                        callback_data=callback_data
                    )
                )

        rows = [buttons[i:i + row_width] for i in range(0, len(buttons), row_width)]
        markup = InlineKeyboardMarkup()
        markup.keyboard = rows

        self.sender.set_reply_markup(markup)  # type: ignore
        self.handler.set_callback_functions(callback_functions)

    def inline_keyboard[Caption: str, Value](self, keyboard: dict[Caption, Value], row_width: int = 1) -> Callable[[Callable[[Message, Value], None]], None]:
        """
        Decorator to attach an inline keyboard to the chain.

        Each button is mapped to a callback that calls the decorated 
        function with the button's associated value.

        ---
        ## Example:
        ```
        @self.chain.inline_keyboard({
            # label: value
            # str  : Any
            "Red": (255, 0, 0),
            "Green": (0, 255, 0),
            "Blue": (0, 0, 255),
        }, row_width=3)
        def _(message, value: tuple[int, int, int]) -> None:
            r, g, b = value
            print(f"You selected RGB color: ({r}, {g}, {b})")
        ```
        ---
        Args:
            keyboard (dict[str, Value]): A dictionary mapping button captions to values.
            row_width (int): Number of buttons per row (default = 1).
        """
        def wrapper(func: Callable[[Message, Value], None]) -> None:
            callback_functions: dict[str, Callable[[Message], Any]] = {}
            buttons: list[InlineKeyboardButton] = []

            def get_callback(value: Value) -> Callable[[Message], None]:
                def callback(message: Message) -> None:
                    func(message, value)
                return callback

            for i, (caption, value) in enumerate(keyboard.items()):
                callback_data = f"button_{i}_{random.randint(1000, 9999)}"
                callback_functions[callback_data] = get_callback(value)
                buttons.append(
                    InlineKeyboardButton(
                        text=caption,
                        callback_data=callback_data
                    )
                )

            rows = [buttons[i:i + row_width] for i in range(0, len(buttons), row_width)]
            markup = InlineKeyboardMarkup()
            markup.keyboard = rows

            self.sender.set_reply_markup(markup)  # type: ignore
            self.handler.set_callback_functions(callback_functions)

        return wrapper
    
    def set_entry_suggestions(self, keyboard: dict[str, str] | list[str], row_width: int = 1) -> None:
        """
        Sets reply suggestions as inline buttons below the message input field.
        These buttons act as quick replies, and send the corresponding `callback_data` when clicked.

        ---

        ## Example:
        ```
        # Receive text message:
        @self.chain.entry_text()
        def name_handler(message, name: str):
            print(name)

        # Inline keyboard with suggested options:
        self.chain.set_entry_suggestions(["Suggestion 1", "Suggestion 2"])
        ```
        ---

        Args:
            keyboard (dict[Caption, Value]): A dictionary where each key is the button's visible text (caption),
                                            and each value is the string to send as callback_data.
            row_width (int, optional): Number of buttons per row. Defaults to 1.
        """
        
        buttons: list[InlineKeyboardButton] = []

        if isinstance(keyboard, list):
            keyboard = {c: c for c in keyboard}

        for caption, value in keyboard.items(): 
            buttons.append(
                InlineKeyboardButton(
                    text=caption,
                    callback_data=value
                )
            )

        rows = [buttons[i:i + row_width] for i in range(0, len(buttons), row_width)]
        markup = InlineKeyboardMarkup()
        markup.keyboard = rows

        self.sender.set_reply_markup(markup)  # type: ignore

    def entry(self, 
              filter_message: Callable[[Message], bool] | None=None,
              delete_user_response: bool=False) -> Callable[[Callable[[Message], Any]], None]:
        """
        Decorator for registering an entry callback with optional message filtering.

        ---
        ## Example:
        ```
        # Receive any message type:
        @self.chain.entry(
            filter_message=lambda message: bool(message.text),
            delete_user_response=True)
        def handler(message):
            print(message.text)
        ```

        ## Example 2 (Cancel button):
        ```python
        # Receive any message type:
        @self.chain.entry()
        def handler(message):
            print(message.text)

        self.chain.set_inline_keyboard(
            {   
                "🚫 Cancel": self.display_cancel,
            }
        )
        ```
        ---

        Args:
            filter_message (Callable[[Message], bool] | None): 
                A filter function that takes a Message and returns True if it should be processed.
            delete_user_response (bool): 
                If True, deletes the user's message after receiving it.
        """
        def wrapper(func: Callable[[Message], Any]) -> None:
            def callback(message: Message) -> bool:
                if delete_user_response:
                    self.sender.delete_message(message, True)
                    
                if filter_message and not filter_message(message):
                    return False
                
                self._cancel_timeout()
                func(message)
                return True
            
            self.handler.set_entry_callback(callback)

        return wrapper 
    
    def entry_text(self, 
              filter_message: Callable[[Message, str], bool] | None=None,
              delete_user_response: bool=False) -> Callable[[Callable[[Message, str], Any]], None]:
        """
        Decorator for registering a text-only entry callback with optional message filtering.

        ---
        ## Example:
        ```
        @self.chain.entry_text(
            filter_message=lambda _, name: " " not in name)
        def name_handler(message, name: str):
            print(name)
        ```
        ## Example 2 (Suggestions):
        ```
        # Receive text message:
        @self.chain.entry_text()
        def name_handler(message, name: str):
            print(name)

        # Add inline keyboard with suggested options:
        self.chain.set_entry_suggestions(["Romashka", "NotRomashka"])
        ```
        ---

        Args:
            filter_message (Callable[[Message, str], bool] | None): 
                A filter function that takes a Message and its text, 
                returns True if it should be processed.
            delete_user_response (bool): 
                If True, deletes the user's message after receiving it.
        """
        def wrapper(func: Callable[[Message, str], Any]) -> None:
            def callback(message: Message) -> bool:
                if delete_user_response:
                    self.sender.delete_message(message, True)

                if not message.text:
                    return False # Only text messages
                    
                if filter_message and not filter_message(message, message.text):
                    return False
                
                self._cancel_timeout()
                func(message, message.text)
                return True
            
            self.handler.set_entry_callback(callback)

        return wrapper
    
    def entry_photo(self, 
              filter_message: Callable[[Message, list[telebot.types.PhotoSize]], bool] | None=None,
              delete_user_response: bool=False) -> Callable[[Callable[[Message, list[telebot.types.PhotoSize]], Any]], None]:
        """
        Decorator for registering a callback that only processes messages containing photos.
        Optionally applies a custom filter or deletes the user's message.

        ---
        ## Example:
        ```
        @self.chain.entry_photo()
        def save_photos(message: Message, photos: list[telebot.types.PhotoSize]):
            for i, photo in enumerate(photos):
                file_info = bot.get_file(photo.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                filename = f"{message.message_id}_{i}.jpg"
                with open(filename, "wb") as f:
                    f.write(downloaded_file)
        ```
        ---

        Args:
            filter_message (Callable[[Message, list[telebot.types.PhotoSize]], bool] | None): 
                A custom filter function that takes a Message and its list of PhotoSize objects. 
                Returns True if the message should be processed.
            delete_user_response (bool): 
                If True, the user's photo message will be deleted after being received.
        """
        def wrapper(func: Callable[[Message, list[telebot.types.PhotoSize]], Any]) -> None:
            def callback(message: Message) -> bool:
                if delete_user_response:
                    self.sender.delete_message(message, True)

                if not message.photo:
                    return False # Only photos
                    
                if filter_message and not filter_message(message, message.photo):
                    return False
                
                self._cancel_timeout()
                func(message, message.photo)
                return True
            
            self.handler.set_entry_callback(callback)

        return wrapper
    
    def entry_document(self, 
              filter_message: Callable[[Message, telebot.types.Document], bool] | None=None,
              allowed_extensions: tuple[str, ...] | None = None,
              delete_user_response: bool=False) -> Callable[[Callable[[Message, telebot.types.Document], Any]], None]:
        """
        Decorator for registering a callback that processes messages containing documents.

        This decorator allows filtering by file extensions, applying a custom filter, 
        and optionally deleting the user's document message after processing.

        ---
        ## Example:
        ```
        @self.chain.entry_document(allowed_extensions=(".zip",))
        def doc_handler(message, document: telebot.types.Document):
            print(document.file_name, document)
        ```
        ---

        Args:
            filter_message (Callable[[Message, Document], bool] | None): 
                Optional function to filter messages. Receives the message and document,
                should return True if the message should be processed.
            allowed_extensions (tuple[str, ...] | None):
                Only documents with these file extensions will be processed.
                Example: (".txt", ".js")
                If None, all document types are allowed.
            delete_user_response (bool): 
                If True, deletes the user's document message after it is received.
        """
        def wrapper(func: Callable[[Message, telebot.types.Document], Any]) -> None:
            def callback(message: Message) -> bool:
                if delete_user_response:
                    self.sender.delete_message(message, True)

                if not message.document:
                    return False # only documents
                
                if message.content_type != 'document':
                    return False # only documents
                
                if allowed_extensions and not str(message.document.file_name).endswith(allowed_extensions):
                    return False # only allowed_extensions
                    
                if filter_message and not filter_message(message, message.document):
                    return False # only filtered
                
                self._cancel_timeout()
                func(message, message.document)
                return True # success
            
            self.handler.set_entry_callback(callback)

        return wrapper
    
    def entry_text_document(self, 
              filter_message: Callable[[Message, TextDocument], bool] | None=None,
              allowed_extensions: tuple[str, ...] = (".txt",),
              encoding: str | None = None,
              decoding_errors: str = "strict",
              delete_user_response: bool=False) -> Callable[[Callable[[Message, TextDocument], Any]], None]:
        """
        Decorator for registering a callback that processes text-based documents.

        This decorator automatically downloads the document, detects or applies a
        specified encoding, decodes the text, wraps it in a TextDocument object, 
        and passes it to the callback.

        ---
        ## Example:
        ```
        # Receive a text document (Telekit auto-detects encoding):
        @self.chain.entry_text_document(allowed_extensions=(".txt", ".js", ".py"))
        def text_document_handler(message, text_document: telekit.types.TextDocument):
            print(
                text_document.text,      # "Example\\n..."
                text_document.file_name, # "example.txt"
                text_document.encoding,  # "utf-8"
                text_document.document   # <telebot.types.Document>
            )
        ```
        ---

        Args:
            filter_message (Callable[[Message, TextDocument], bool] | None):
                Optional function to filter messages. Receives the message and TextDocument,
                should return True if the message should be processed.
            allowed_extensions (tuple[str, ...]):
                File extensions that are allowed. Defaults to (".txt",).
            encoding (str | None):
                Encoding to decode the document. If None, charset-normalizer is used to detect it.
            decoding_errors (str):
                Error handling strategy for decoding. Defaults to "strict".
                Other options: "ignore", "replace".
            delete_user_response (bool):
                If True, deletes the user's document message after it is received.
        """
        def wrapper(func: Callable[[Message, TextDocument], Any]) -> None:
            def callback(message: Message) -> bool:
                if delete_user_response:
                    self.sender.delete_message(message, True)

                if not message.document:
                    return False # only documents
                
                if message.content_type != 'document':
                    return False # only documents
                
                file_name = str(message.document.file_name)
                
                if not file_name.endswith(allowed_extensions):
                    return False # only allowed_extensions
                
                try:
                    file_info = self.bot.get_file(message.document.file_id)
                    downloaded_file = self.bot.download_file(str(file_info.file_path))

                    if not encoding:
                        results = charset_normalizer.from_bytes(downloaded_file)
                        best_guess = results.best()

                        if not best_guess:
                            return False # unknown encoding
                        
                        _encoding = best_guess.encoding
                    else:
                        _encoding = encoding

                    text = downloaded_file.decode(_encoding, decoding_errors)
                except Exception as extension:
                    print(extension)
                    return False
                
                text_doc = TextDocument(
                    message, message.document,
                    file_name, _encoding, text
                )
                    
                if filter_message and not filter_message(message, text_doc):
                    return False # only filtered
                
                self._cancel_timeout()
                func(message, text_doc)
                return True # success
            
            self.handler.set_entry_callback(callback)

        return wrapper

    def entry_location(
        self,
        filter_message: Callable[[Message, telebot.types.Location], bool] | None = None,
        delete_user_response: bool = False
    ) -> Callable[[Callable[[Message, telebot.types.Location], Any]], None]:
        """
        Decorator for registering a callback that processes messages containing a location.

        ---
        ## Example:
        ```
        @self.chain.entry_location()
        def location_handler(message, location: telebot.types.Location):
            print(location.latitude, location.longitude)
        ```
        ---

        Args:
            filter_message: Optional function to filter messages. Receives message and location,
                            should return True if the message should be processed.
            delete_user_response: If True, deletes the user's location message after it is received.
        """
        def wrapper(func: Callable[[Message, telebot.types.Location], Any]) -> None:
            def callback(message: Message) -> bool:
                if not message.location:
                    return False  # only location messages
                
                loc = message.location

                if filter_message and not filter_message(message, loc):
                    return False  # only filtered
                
                if delete_user_response:
                    self.sender.delete_message(message, True)
                
                self._cancel_timeout()
                func(message, loc)
                return True  # success
            
            self.handler.set_entry_callback(callback)
        return wrapper
    
    # -------------------------------------------
    # Timeouts
    # -------------------------------------------

    def on_timeout(self, seconds: int = 0, minutes: int = 0, hours: int = 0):
        """
        Decorator for registering a callback to be executed after a timeout.

        ---

        ## Usage:
        ```
            @chain.timeout(seconds=10)
            def my_callback():
                ...
        ```
        ---
        
        """
        def decorator(func: Callable):
            self.set_timeout(func, seconds=seconds, minutes=minutes, hours=hours)
            return func
        return decorator
    
    def set_timeout(self, callback: Callable | None, seconds: int=0, minutes: int=0, hours: int=0):
        if callback is None:
            callback = lambda: None
        self._set_timeout_callback(callback)
        self._set_timeout_time(seconds, minutes, hours)
    
    def _set_timeout_callback(self, callback: Callable):
        def wrapper():
            self.handler.reset()
            callback()
        self.handler.set_cancel_timeout_callback(self._cancel_timeout)
        self._timeout_handler.set_callback(wrapper)

    def _set_timeout_time(self, seconds: int=0, minutes: int=0, hours: int=0):
        self._timeout_handler.set_time(seconds, minutes, hours)
    
    def _start_timeout(self):
        self._timeout_handler.maybe_start()

    def _cancel_timeout(self):
        self._timeout_handler.cancel()

    def set_always_edit_previous_message(self, value: bool=True) -> None:
        """
        Sets whether the chain should always edit the previous message 
        instead of sending a new one.

        >>> self.chain.set_always_edit_previous_message(True)

        Args:
            value (bool): If True, edits previous messages by default.
        """
        self.always_edit_previous_message = value

    def send(self) -> Message | None:
        """
        Sends a new message or edits the previous message if enabled.

        >>> self.chain.send()

        Returns:
            Message | None: The sent or edited message.
        """
        self._start_timeout()
        self.handler.handle_next_message()

        if self.always_edit_previous_message:
            self.edit_previous_message()

        message = self.sender.send_or_handle_error()
        self._set_previous_message(message)
        return message
    
    def edit(self) -> Message | None:
        """
        Edits the previously sent message.

        >>> self.chain.edit()

        Returns:
            Message | None: The edited message.
        """
        self.edit_previous_message()
        return self.send()
    
    def _set_previous_message(self, message: Message | None) -> None:
        self._previous_message = message

        if self.parent:
            self.parent._set_previous_message(message)
    
    def get_previous_message(self) -> Message | None:
        """
        Returns the previous message sent by the chain.

        >>> self.chain.get_previous_message()
        
        Returns:
            Message | None: The previous message or None if no message was sent
        """
        if self._previous_message:
            return self._previous_message
        elif self.parent:
            return self.parent.get_previous_message()
        else:
            return None
        
    def edit_previous_message(self) -> None:
        """
        Edits the previous message sent by the chain with the current sender's message

        >>> self.chain.edit_previous_message()

        is equal to:

        >>> self.chain.sender.set_edit_message(self.chain.get_previous_message())
        """
        self.sender.set_edit_message(self.get_previous_message())
    
    def set_parent(self, parent: 'Chain') -> None:
        """
        Sets the parent chain for this chain.

        Args:
            parent (Chain): The parent chain to be set.
        """
        self.parent = parent
        self.always_edit_previous_message = parent.always_edit_previous_message

    def __call__(self, message: Message | None = None):
        self.send()
    
    def get_bot(self) -> telebot.TeleBot:
        """
        Returns the bot instance associated with this chain.
        
        Returns:
            telebot.TeleBot: The bot instance.
        """
        return self.bot

    @classmethod
    def get_chain_factory(cls, chat_id: int) -> Callable[[], 'Chain']:
        def message_factory() -> Chain:
            return cls(chat_id)
        return message_factory
    
    @classmethod
    def get_children_factory(cls, chat_id: int) -> Callable[[Any], 'Chain']:
        def children_factory(parent: Chain | None=None) -> Chain:
            chain = cls(chat_id)
            if parent:
                chain.set_parent(parent)
            return chain
        return children_factory