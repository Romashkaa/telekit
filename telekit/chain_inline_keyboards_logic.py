# Copyright (c) 2025 Ving Studio, Romashka
# Licensed under the MIT License. See LICENSE file for full terms.

# Standard library
import random
import typing
from typing import Callable, Any
from collections.abc import Iterable

# Third-party packages
from telebot.types import (
    Message, 
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from .chain_base import ChainBase

if typing.TYPE_CHECKING:
    from .chain import Chain # only for type hints

class ChainInlineKeyboardLogic(ChainBase):
    def set_inline_keyboard(
            self, 
            keyboard: dict[str, 'Chain' | Callable[..., Any] | str], 
            row_width: int | Iterable[int] = 1
        ) -> None:
        """
        Sets an inline keyboard for the chain, where each button triggers the corresponding action.
        Every button calls its associated function with the message as an argument (if applicable).
        
        ---
        ### Example 1 (callback types):
        ```
        self.chain.set_inline_keyboard(
            {   
                # When the user clicks this button, `prompt()` will be executed
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
            keyboard (dict[str, Callable[..., Any] | str]): A dictionary where keys are button captions
                and values are functions to be called when the button is clicked.
            row_width (int | Iterable[int]): Number of buttons per row; can be a single value or an iterable that defines the number of buttons in each row in order (default = 1).
        """
        callback_functions: dict[str, Callable[[Message], Any]] = {}
        buttons: list[InlineKeyboardButton] = []

        def wrap_callback(callback: Callable[..., None]):
            def wrapper(*args):
                self._got_response_or_callback()

                if self._accepts_parameter(callback):
                    callback(*args)
                else:
                    callback()
            return wrapper

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
                callback_functions[callback_data] = wrap_callback(callback)
                buttons.append(
                    InlineKeyboardButton(
                        text=caption,
                        callback_data=callback_data
                    )
                )

        markup = InlineKeyboardMarkup()
        markup.keyboard = self._build_keyboard_rows(buttons, row_width)

        self.sender.set_reply_markup(markup)
        self.handler.set_callback_functions(callback_functions)

    def inline_keyboard[Caption: str, Value](
            self, 
            keyboard: dict[Caption, Value], 
            row_width: int | Iterable[int] = 1
        ) -> Callable[[Callable[[Message, Value], None]], None]:
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
            row_width (int | Iterable[int]): Number of buttons per row; can be a single value or an iterable that defines the number of buttons in each row in order (default = 1).
        """
        def wrapper(func: Callable[[Message, Value], None]) -> None:
            callback_functions: dict[str, Callable[[Message], Any]] = {}
            buttons: list[InlineKeyboardButton] = []

            def get_callback(value: Value) -> Callable[[Message], None]:
                def callback(message: Message) -> None:
                    self._got_response_or_callback()
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

            markup = InlineKeyboardMarkup()
            markup.keyboard = self._build_keyboard_rows(buttons, row_width)

            self.sender.set_reply_markup(markup)
            self.handler.set_callback_functions(callback_functions)

        return wrapper
    
    def set_entry_suggestions(
            self, 
            keyboard: dict[str, str] | list[str], 
            row_width: int | Iterable[int] = 1
        ) -> None:
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

        ```
        # (OR) Inline keyboard with suggested options and custom labels:
        self.chain.set_entry_suggestions({"Label": "Suggestion"})
        ```
        ---

        Args:
            keyboard (dict[Caption, Value]): A dictionary where each key is the button's visible text (caption),
                                            and each value is the string to send as callback_data.
            row_width (int | Iterable[int]): Number of buttons per row; can be a single value or an iterable that defines the number of buttons in each row in order (default = 1).
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

        markup = InlineKeyboardMarkup()
        markup.keyboard = self._build_keyboard_rows(buttons, row_width)

        self.sender.set_reply_markup(markup)

    def _build_keyboard_rows(
        self,
        buttons: list[InlineKeyboardButton],
        row_width: int | Iterable[int],
    ) -> list[list[InlineKeyboardButton]]:
        rows: list[list[InlineKeyboardButton]] = []

        if isinstance(row_width, int):
            return [
                buttons[i:i + row_width]
                for i in range(0, len(buttons), row_width)
            ]

        index = 0
        widths = list(row_width)

        for width in widths:
            if index >= len(buttons):
                break
            rows.append(buttons[index:index + width])
            index += width

        # use the last width for remaining buttons
        if index < len(buttons):
            last_width = widths[-1]
            while index < len(buttons):
                rows.append(buttons[index:index + last_width])
                index += last_width

        return rows