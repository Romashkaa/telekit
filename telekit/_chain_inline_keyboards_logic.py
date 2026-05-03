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

# Standard library
import random
import typing
from typing import Callable, Any
from collections.abc import Iterable

# Third-party packages
from telebot.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from ._callback_query_handler import CallbackQueryHandler
from ._inline_buttons import InlineButton, CallbackButton
from ._chain_base import ChainBase, library

if typing.TYPE_CHECKING:
    from ._chain import Chain # only for type hints

class ChainInlineKeyboardLogic(ChainBase):
    def set_inline_keyboard(
            self, 
            keyboard: dict[str, Any], 
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
        button_callbacks: dict[str, Callable[[CallbackQuery], None]] = {}
        buttons: list[InlineKeyboardButton] = []

        for i, (caption, callback) in enumerate(keyboard.items()):
            if isinstance(callback, str):
                buttons.append(InlineKeyboardButton(caption, url=callback))
            elif isinstance(callback, InlineButton) and not isinstance(callback, CallbackButton):
                buttons.append(callback._compile(caption))
            else:
                if isinstance(callback, CallbackButton):
                    invoker = callback.build_invoker(self._cancel_timeout_and_handlers)
                else:
                    invoker = CallbackButton.create_invoker(callback, self._cancel_timeout_and_handlers)

                callback_data = CallbackQueryHandler.inline_button(f"{i}:{random.randint(1000, 9999)}")
                button_callbacks[callback_data] = invoker
                buttons.append(
                    InlineKeyboardButton(
                        text=caption,
                        callback_data=callback_data,
                        **invoker._kwargs # pyright: ignore[reportArgumentType]
                    )
                )

        markup = InlineKeyboardMarkup()
        markup.keyboard = self._build_keyboard_rows(buttons, row_width)

        self.sender.set_reply_markup(markup)
        self._handler.set_button_callbacks(button_callbacks)

    def inline_keyboard[Caption: str, Value](
            self, 
            keyboard: dict[Caption, Value],
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
            callback_functions: dict[str, Callable[[CallbackQuery], None]] = {}
            buttons: list[InlineKeyboardButton] = []

            for index, (caption, value) in enumerate(keyboard.items()):
                if enable_special_buttons and isinstance(value, InlineButton) and not isinstance(value, CallbackButton):
                    buttons.append(value._compile(caption))
                else:
                    if isinstance(value, CallbackButton):
                        invoker = value.build_invoker(self._cancel_timeout_and_handlers)
                    else:
                        invoker = self._get_invoker_with_argument(func, value)

                    callback_data = CallbackQueryHandler.inline_button(f"{index}:{random.randint(1000, 9999)}")
                    callback_functions[callback_data] = invoker

                    kwargs: dict[str, Any] = getattr(invoker, "_kwargs", None) or {}

                    buttons.append(
                        InlineKeyboardButton(
                            text=caption,
                            callback_data=callback_data,
                            **kwargs
                        )
                    )

            markup = InlineKeyboardMarkup()
            markup.keyboard = self._build_keyboard_rows(buttons, row_width)

            self.sender.set_reply_markup(markup)
            self._handler.set_button_callbacks(callback_functions)

        return wrapper
    
    def inline_choice(
            self, 
            choices: list[Any] | tuple[Any, ...] | dict[str, Any | InlineButton],
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
        callback_functions: dict[str, Callable[[CallbackQuery], None]] = {}
        buttons: list[InlineKeyboardButton] = []

        if not isinstance(choices, dict):
            for c in choices:
                if type(c).__str__ is object.__str__:
                    library.warning(
                        f"{type(c).__name__} does not implement __str__. "
                        f"Consider passing a dict with explicit labels.",
                        stacklevel=3
                    )
            choices = {str(c): c for c in choices}

        for index, (caption, value) in enumerate(choices.items()):
            if enable_special_buttons and isinstance(value, InlineButton) and not isinstance(value, CallbackButton):
                buttons.append(value._compile(caption))
            else:
                if isinstance(value, CallbackButton):
                    invoker = value.build_invoker(self._cancel_timeout_and_handlers)
                else:
                    invoker = self._get_invoker_with_argument(func, value)

                callback_data = CallbackQueryHandler.inline_button(f"{index}:{random.randint(1000, 9999)}")
                callback_functions[callback_data] = invoker

                kwargs: dict[str, Any] = getattr(invoker, "_kwargs", None) or {}

                buttons.append(
                    InlineKeyboardButton(
                        text=caption,
                        callback_data=callback_data,
                        **kwargs
                    )
                )

        markup = InlineKeyboardMarkup()
        markup.keyboard = self._build_keyboard_rows(buttons, row_width)

        self.sender.set_reply_markup(markup)
        self._handler.set_button_callbacks(callback_functions)
    
    def set_entry_suggestions(
            self, 
            keyboard: dict[str, str] | list[str], 
            *,
            row_width: int | Iterable[int] = 1
        ) -> None:
        """
        Sets reply suggestions as inline buttons below the message.
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
            for suggestion in keyboard:
                buttons.append(InlineButton.Suggest(suggestion)._compile(suggestion))
        else:
            for caption, suggestion in keyboard.items():
                buttons.append(InlineButton.Suggest(suggestion)._compile(caption))

        markup = InlineKeyboardMarkup()
        markup.keyboard = self._build_keyboard_rows(buttons, row_width)

        self.sender.set_reply_markup(markup)

    def _get_invoker_with_argument(self, callback: Callable, argument: Any, query_answer: tuple[str, bool] | None = None) -> Callable[[CallbackQuery], None]:
        def invoker(call: CallbackQuery) -> None:
            self._cancel_timeout_and_handlers()
            callback(argument)
            self._answer_callback_query(call, query_answer)

        return invoker
    
    def _get_invoker(self, callback: Callable[..., None], query_answer: tuple[str, bool] | None = None) -> Callable[[CallbackQuery], None]:
        def invoker(call: CallbackQuery):
            self._cancel_timeout_and_handlers()
            callback()
            self._answer_callback_query(call, query_answer)

        return invoker
    
    def _answer_callback_query(self, call: CallbackQuery, query_answer: tuple[str, bool] | None = None):
        if query_answer is None:
            self.bot.answer_callback_query(call.id)
        else:
            self.bot.answer_callback_query(
                call.id, 
                text=query_answer[0], 
                show_alert=query_answer[1]
            )

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