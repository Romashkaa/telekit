# Copyright (c) 2025 Ving Studio, Romashka
# Licensed under the MIT License. See LICENSE file for full terms.

# Standard library
import random
import typing
from typing import Callable, Any, overload, Literal
from collections.abc import Iterable

# Third-party packages
from telebot.types import (
    Message, 
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from ._inline_buttons import InlineButton
from ._chain_base import ChainBase

if typing.TYPE_CHECKING:
    from ._chain import Chain # only for type hints

class ChainInlineKeyboardLogic(ChainBase):
    def set_inline_keyboard(
            self, 
            keyboard: dict[str, Callable[[], Any] | InlineButton | str], 
            *,
            row_width: int | Iterable[int] = 1
        ) -> None:
        """
        Sets an inline keyboard for the chain, where each button triggers the corresponding action.
        
        ---
        ### Example
        ```
        from telekit.types import LinkButton, CopyTextButton

        self.chain.set_inline_keyboard(
            {   
                # When the user clicks this button, `change_name()` will be executed
                "Change": change_name,
                # When the user clicks this button, this lambda function will run
                "Okay": lambda: print("User: Okay!"),
                # When the user clicks this button, this method will be executed
                "Reload": self.reload,
                # Can even be a link (`str` or `LinkButton` object)
                "PyPi": "https://pypi.org/project/telekit/",
                "GitHub": LinkButton("https://github.com/Romashkaa/telekit"),
                # Or copy button
                "Copy Text": CopyTextButton("Text to copy")
            }, row_width=(3, 2, 1)
        )
        ```
        ### Result
        ```
        ╭────────────┬──────────┬──────────╮
        │   Change   │   Okay   │  Reload  │
        ├────────────┴────┬─────┴──────────┤
        │       PyPi      │     GitHub     │
        ├─────────────────┴────────────────┤
        │            Copy Text             │
        ╰──────────────────────────────────╯
        ```
        ---
        Args:
            keyboard (`dict[str, Callable[[], Any]` | `InlineButton` | `str`]): A dictionary where keys are 
                button captions and values are callbacks, `InlineButton` objects, or URL strings.
            row_width (`int` | `Iterable[int]`): Number of buttons per row (default = 1); can be a single value 
                or an iterable defining the buttons count for each row.
        """
        callback_functions: dict[str, Callable[[Message], Any]] = {}
        buttons: list[InlineKeyboardButton] = []

        for i, (caption, callback) in enumerate(keyboard.items()):
            if isinstance(callback, str):
                buttons.append(InlineKeyboardButton(caption, url=callback))
            elif isinstance(callback, InlineButton):
                buttons.append(callback._compile(caption))
            else:
                callback_data = f"button_{i}_{random.randint(1000, 9999)}"
                callback_functions[callback_data] = self._get_callback(callback)
                buttons.append(
                    InlineKeyboardButton(
                        text=caption,
                        callback_data=callback_data
                    )
                )

        markup = InlineKeyboardMarkup()
        markup.keyboard = self._build_keyboard_rows(buttons, row_width)

        self.sender.set_reply_markup(markup)
        self._handler.set_callback_functions(callback_functions)

    def inline_keyboard[Caption: str, Value](
            self, 
            keyboard: dict[Caption, Value],
            *,
            row_width: int | Iterable[int] = 1,
            enable_special_buttons: bool = True
        ) -> Callable[[Callable[[Value], None]], None]:
        """
        Decorator to attach an inline keyboard with associated values to the chain.

        Each button is mapped to a callback that calls the decorated 
        function with the button's associated value.

        ---
        ## Example:
        ```
        @self.chain.inline_keyboard({
            "Red": (255, 0, 0),
            "Green": (0, 255, 0),
            "Blue": (0, 0, 255),
        }, row_width=3)
        def _(value: tuple[int, int, int]) -> None:
            r, g, b = value
            print(f"You selected RGB color: ({r}, {g}, {b})")
        ```
        ---
        Args:
            keyboard (`dict[str, Value]`): A dictionary mapping button captions to values.
            row_width (`int` | `Iterable[int]`): Number of buttons per row (default = 1); can be a single value or an iterable that defines the number of buttons in each row in order.
            enable_special_buttons (`bool`): If True, `InlineButton` instances (e.g., LinkButton) are compiled into functional buttons. If False, they are treated as plain values and passed to wrapped function.
        """
        def wrapper(func: Callable[[Value], None]) -> None:
            callback_functions: dict[str, Callable[[Message], Any]] = {}
            buttons: list[InlineKeyboardButton] = []

            for index, (caption, value) in enumerate(keyboard.items()):
                if enable_special_buttons and isinstance(value, InlineButton):
                    buttons.append(value._compile(caption))
                else:
                    callback_data = f"button_{index}_{random.randint(1000, 9999)}"
                    callback_functions[callback_data] = self._get_callback_with_argument(func, value)
                    buttons.append(
                        InlineKeyboardButton(
                            text=caption,
                            callback_data=callback_data
                        )
                    )

            markup = InlineKeyboardMarkup()
            markup.keyboard = self._build_keyboard_rows(buttons, row_width)

            self.sender.set_reply_markup(markup)
            self._handler.set_callback_functions(callback_functions)

        return wrapper
    
    def inline_choice(
            self, 
            choices: list[Any] | tuple[Any, ...] | dict[str, Any | InlineButton],
            *,
            row_width: int | Iterable[int] = 1,
            enable_special_buttons: bool = True
        ) -> Callable[[Callable[[Any], None]], None]:
        """
        Decorator to attach an inline choice keyboard to the chain.

        ---
        ## Example:
        ```python
        @self.chain.inline_choice(["Option A", "Option B"])
        def _(choice: str) -> None:
            print(f"Selected: {choice}")
        ```
        ---
        Args:
            choices: A collection of options. 
                - If `list` or `tuple`: elements serve as both labels (via `str()`) and values.
                - If `dict`: keys are button labels, and values are the associated data or (if `enable_special_buttons` is True) `InlineButton` objects.
            row_width (`int` | `Iterable[int]`): Buttons per row (default = 1); can be a single value or an iterable that defines the number of buttons in each row in order.
            enable_special_buttons (`bool`): If True, `InlineButton` instances (e.g., LinkButton) are compiled into functional buttons. If False, they are treated as plain values and passed to `func`.
        """
        def wrapper(func: Callable[[Any], None]) -> None:
            self.set_inline_choice(
                func=func,
                choices=choices,
                row_width=row_width,
                enable_special_buttons=enable_special_buttons
            )

        return wrapper
    
    def set_inline_choice(
            self,
            func: Callable[[Any], None],
            choices: list[Any] | tuple[Any, ...] | dict[str, Any | InlineButton],
            *,
            row_width: int | Iterable[int] = 1,
            enable_special_buttons: bool = True
        ) -> None:
        """
        Attach an inline choice keyboard to the chain.

        This method generates an inline keyboard based on the provided choices. 
        If a dictionary is provided, keys are used as button labels. 
        Values are either passed to 'func' or compiled into special buttons (like LinkButtons) if enabled.

        ---
        ## Example:
        ```python
        self.chain.set_inline_choice(
            lambda value: print(f"User picked {value}"),
            choices=["Choice 1", "Choice 2"]
        )
        ```
        ---
        Args:
            func (`Callable`): Callback function to execute on choice.
            choices: A collection of options. 
                - If `list` or `tuple`: elements serve as both labels (via `str()`) and values.
                - If `dict`: keys are button labels, and values are the associated data or (if `enable_special_buttons` is True) `InlineButton` objects.
            row_width (`int` | `Iterable[int]`): Layout configuration for buttons.
            enable_special_buttons (`bool`): If True, `InlineButton` instances (e.g., LinkButton) are compiled into functional buttons. If False, they are treated as plain values and passed to `func`.
        """
        callback_functions: dict[str, Callable[[Message], Any]] = {}
        buttons: list[InlineKeyboardButton] = []

        if not isinstance(choices, dict):
            choices = {str(c): c for c in choices}

        for index, (caption, value) in enumerate(choices.items()):
            if enable_special_buttons and isinstance(value, InlineButton):
                buttons.append(value._compile(caption))
            else:
                callback_data = f"button_{index}_{random.randint(1000, 9999)}"
                callback_functions[callback_data] = self._get_callback_with_argument(func, value)
                buttons.append(
                    InlineKeyboardButton(
                        text=caption,
                        callback_data=callback_data
                    )
                )

        markup = InlineKeyboardMarkup()
        markup.keyboard = self._build_keyboard_rows(buttons, row_width)

        self.sender.set_reply_markup(markup)
        self._handler.set_callback_functions(callback_functions)
    
    def set_entry_suggestions(
            self, 
            keyboard: dict[str, str] | list[str], 
            *,
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
            keyboard (`dict[Caption, Value]`): A dictionary where each key is the button's visible text (caption),
                                            and each value is the string to send as callback_data.
            row_width (`int` | `Iterable[int]`): Number of buttons per row (default = 1); can be a single value or an iterable that defines the number of buttons in each row in order.
        Raises:
            ValueError: If the callback_data (suggestion length) exceeds the 64-byte Telegram limit.
        """
        
        buttons: list[InlineKeyboardButton] = []

        if isinstance(keyboard, list):
            keyboard = {c: c for c in keyboard}

        for caption, value in keyboard.items():
            if not self._is_valid_telegram_callback(value):
                raise ValueError(
                    f"Callback data for button '{caption}' is too long! "
                    f"Telegram limit is 64 bytes, but yours is {len(value.encode('utf-8'))} bytes. "
                    f"Value: '{value}'"
                )

            buttons.append(
                InlineKeyboardButton(
                    text=caption,
                    callback_data=value
                )
            )

        markup = InlineKeyboardMarkup()
        markup.keyboard = self._build_keyboard_rows(buttons, row_width)

        self.sender.set_reply_markup(markup)

    def _get_callback_with_argument(self, func: Callable, argument: Any, include_message: bool=False) -> Callable[[Message], None]:
        def callback(message: Message) -> None:
            self._cancel_timeout_and_handlers()

            if include_message:
                func(message, argument)
            else:
                func(argument)

        return callback
    
    def _get_callback(self, func: Callable[..., None], include_message: bool=False):
        def callback(message: Message):
            self._cancel_timeout_and_handlers()

            if include_message:
                func(message)
            else:
                func()

        return callback

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
    
    def _is_valid_telegram_callback(self, data: str) -> bool:
        byte_size = len(data.encode('utf-8'))
        return 1 <= byte_size <= 64