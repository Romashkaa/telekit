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

    def set_inline_keyboard(self, keyboard: dict[str, 'Chain' | Callable[..., Any] | str], row_width: int = 1) -> None:
        """
        Sets an inline keyboard for the chain with buttons that call the corresponding functions.
        Each button will call the function with the message as an argument.

        `Callable[..., Any]` may be:
            - `Callable[[Message], Any]` — accepts a Message object, or 
            - `Callable[[], Any]` — takes no arguments.
        
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

        Args:
            keyboard (dict[str, Value]): A dictionary mapping button captions to values.
            row_width (int): Number of buttons per row (default = 1).

        Returns:
            Callable[[Callable[[Message, Value], None]], None]:
                A decorator function that registers the button callbacks.
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

        Args:
            filter_message (Callable[[Message], bool] | None): 
                A filter function that takes a Message and returns True if it should be processed.
            delete_user_response (bool): 
                If True, deletes the user's message after receiving it.

        Returns:
            Callable[[Callable[[Message], Any]], None]: 
                A decorator function that registers the entry callback.
        """
        def wrapper(func: Callable[[Message], Any]) -> None:
            def callback(message: Message) -> bool:
                if delete_user_response:
                    self.sender.delete_message(message)
                    
                if filter_message and not filter_message(message):
                    return False
                
                func(message)
                return True
            
            self.handler.set_entry_callback(callback)

        return wrapper 
    
    def entry_text(self, 
              filter_message: Callable[[Message, str], bool] | None=None,
              delete_user_response: bool=False) -> Callable[[Callable[[Message, str], Any]], None]:
        """
        Decorator for registering a text-only entry callback with optional message filtering.

        Args:
            filter_message (Callable[[Message, str], bool] | None): 
                A filter function that takes a Message and its text, 
                returns True if it should be processed.
            delete_user_response (bool): 
                If True, deletes the user's message after receiving it.

        Returns:
            Callable[[Callable[[Message, str], Any]], None]: 
                A decorator function that registers the entry callback.
        """
        def wrapper(func: Callable[[Message, str], Any]) -> None:
            def callback(message: Message) -> bool:
                if delete_user_response:
                    self.sender.delete_message(message)

                if not message.text:
                    return False # Only text messages
                    
                if filter_message and not filter_message(message, message.text):
                    return False
                
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

        Args:
            filter_message (Callable[[Message, list[telebot.types.PhotoSize]], bool] | None): 
                A custom filter function that takes a Message and its list of PhotoSize objects. 
                Returns True if the message should be processed.
            delete_user_response (bool): 
                If True, the user's photo message will be deleted after being received.

        Returns:
            Callable[[Callable[[Message, list[telebot.types.PhotoSize]], Any]], None]: 
                A decorator function that registers the photo entry callback.
        """
        def wrapper(func: Callable[[Message, list[telebot.types.PhotoSize]], Any]) -> None:
            def callback(message: Message) -> bool:
                if delete_user_response:
                    self.sender.delete_message(message)

                if not message.photo:
                    return False # Only photos
                    
                if filter_message and not filter_message(message, message.photo):
                    return False
                
                func(message, message.photo)
                return True
            
            self.handler.set_entry_callback(callback)

        return wrapper

    def set_always_edit_previous_message(self, value: bool=True) -> None:
        """
        Sets whether the chain should always edit the previous message 
        instead of sending a new one.

        Args:
            value (bool): If True, edits previous messages by default.
        """
        self.always_edit_previous_message = value

    def send(self) -> Message | None:
        """
        Sends a new message or edits the previous message if enabled.

        Returns:
            Message | None: The sent or edited message.
        """
        self.handler.handle_next_message()

        if self.always_edit_previous_message:
            self.edit_previous_message()

        message = self.sender.send_or_handle_error()
        self._set_previous_message(message)
        return message
    
    def edit(self) -> Message | None:
        """
        Edits the previously sent message.

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