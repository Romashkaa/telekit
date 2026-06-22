from typing import Callable, Any, Literal

from telekit.inline_buttons import *

class InlineKeyboard:
    def __init__(self, inline_keyboard: list[list[tuple[str, InlineButton]]] | None = None):
        self._rows: list[list[tuple[str, InlineButton]]] = []

        if inline_keyboard is not None:
            self._rows.extend(inline_keyboard)

        self._current: list[tuple[str, InlineButton]] = []
        self._grid_width: int = 0

    def row(self, *, when: bool | int = True):
        """
        Finalizes the current row and starts a new one.

        :param when: If `False`, the row is not finalized.
        :type when: `bool`
        """
        if not when:
            return self
        if self._current:
            self._rows.append(self._current)
            self._current = []
        return self
    
    def grid(self, width: int = 1):
        """
        Enable grid mode: buttons added after this call will be
        automatically split into rows of ``width`` buttons each.

        Use together with :meth:`grid_end` to wrap a block of buttons.

        :param width: Number of buttons per row. ``0`` disables grid mode
            (no automatic row breaks).
        :type width: `int`

        Example::

            InlineKeyboard()
                .grid(width=3)
                .add_callback("1", self.on_pick, pass_args=(1,))
                .add_callback("2", self.on_pick, pass_args=(2,))
                .add_callback("3", self.on_pick, pass_args=(3,))
                .add_callback("4", self.on_pick, pass_args=(4,))
                .add_callback("5", self.on_pick, pass_args=(5,))
                .grid_end()
                .add_callback("« Back", self.handle)

        This produces rows of [1, 2, 3], [4, 5], then "« Back" on its own row.
        """
        if width < 0:
            raise ValueError("width must be >= 0")
        self._grid_width = width
        self.row()
        return self

    def grid_end(self):
        """
        Disable grid mode and finalize the current row.

        Calls :meth:`row` automatically so the next buttons added
        outside the grid block start on a fresh row.
        """
        self._grid_width = 0
        self.row()
        return self

    def column(self):
        """
        Enable column mode: every button added after this call
        will automatically be placed on its own row.

        Alias for :meth:`grid` with ``width=1``.

        Use together with :meth:`column_end` to wrap a block of buttons.

        Example::

            InlineKeyboard()
                .column()
                .add_callback("Option A", self.on_a)
                .add_callback("Option B", self.on_b)
                .add_callback("Option C", self.on_c)
                .column_end()
        """
        return self.grid(1)

    def column_end(self):
        """
        Disable column mode and finalize the current row.

        Alias for :meth:`grid_end`.
        """
        return self.grid_end()

    def _grid_count(self) -> int:
        """
        Returns the number of buttons currently in the unfinalized row.
        """
        return len(self._current)

    def _maybe_row(self):
        if self._grid_width and self._grid_count() >= self._grid_width:
            self.row()

    def _compile(self) -> list[list[tuple[str, InlineButton]]]:
        self.row()
        return self._rows
    
    def add(self, text: str, inline_button: InlineButton | None = None, *, when: bool | int = True):
        """
        Adds a button to the current row.

        :param text: The label displayed on the button.
        :type text: `str`

        :param inline_button: The button object to attach. If omitted, a `StaticButton` is used.
        :type inline_button: `InlineButton | None`

        :param when: If `False`, the button is not added.
        :type when: `bool`
        """
        if not when:
            return self
        self._current.append(
            (text, inline_button if inline_button is not None else StaticButton())
        )
        self._maybe_row()
        return self

    def add_callback(
        self,
        text: str,
        callback: Callable[..., Any] | None,
        pass_args: tuple | list | None = None,
        pass_kwargs: dict[str, Any] | None = None,
        *,
        answer_text: str | None = None,
        answer_as_alert: bool = True,
        style: Literal["danger", "success", "primary"] | None | ButtonStyle = None,
        when: bool | int = True
    ):
        """
        Adds a button that triggers a callback function when pressed.

        :param text: The label displayed on the button.
        :type text: `str`

        :param callback: A callable to be executed when the callback query is received.
        :type callback: `Callable[..., Any]`

        :param pass_args: Positional arguments to pass into the callback function.
        :type pass_args: `tuple | list | None`

        :param pass_kwargs: Keyword arguments to pass into the callback function.
        :type pass_kwargs: `dict[str, Any] | None`

        :param answer_text: Optional text to send as an answer to the callback query.
        :type answer_text: `str | None`

        :param answer_as_alert: If `True`, the answer text will be shown as an alert. If `False`, it will be shown as a notification at the top of the chat.
        :type answer_as_alert: `bool`

        :param style: Style of the button. Must be one of `telekit.types.ButtonStyle.DANGER` (red),
              `*.SUCCESS` (green) or `*.PRIMARY` (blue).
              You can also pass these as string values: "danger", "success", "primary".
              If omitted, an client-specific default style is used.
        :type style: `str`

        :param when: If `False`, the button is not added.
        :type when: `bool`

        :param kwargs: Additional keyword arguments passed directly to `InlineKeyboardButton`.
        :type kwargs: `Any`
        """
        if not when:
            return self
        button = CallbackButton(
            callback,
            pass_args, pass_kwargs,
            answer_text=answer_text,
            answer_as_alert=answer_as_alert,
            style=style
        )
        self._current.append((text, button))
        self._maybe_row()
        return self

    def add_link(
        self,
        text: str,
        url: str,
        *,
        style: Literal["danger", "success", "primary"] | None | ButtonStyle = None,
        when: bool | int = True,
        **kwargs
    ):
        """
        Adds a link button that opens a URL when pressed.

        :param text: The label displayed on the button.
        :type text: `str`

        :param url: HTTP or tg:// URL to be opened when the button is pressed. Links tg://user?id= can be used to mention a user by their ID without using a username, if this is allowed by their privacy settings.
        :type url: `str`

        :param style: Style of the button. Must be one of `telekit.types.ButtonStyle.DANGER` (red),
              `*.SUCCESS` (green) or `*.PRIMARY` (blue).
              You can also pass these as string values: "danger", "success", "primary".
              If omitted, an client-specific default style is used.
        :type style: `str`

        :param when: If `False`, the button is not added.
        :type when: `bool`

        :param kwargs: Additional keyword arguments passed directly to `InlineKeyboardButton`.
        :type kwargs: `Any`
        """
        if not when:
            return self
        self._current.append((text, LinkButton(url, style=style, **kwargs)))
        self._maybe_row()
        return self

    def add_contact(
        self,
        text: str,
        user_id: str | int,
        *,
        style: Literal["danger", "success", "primary"] | None | ButtonStyle = None,
        when: bool | int = True,
        **kwargs
    ):
        """
        Adds a button that mentions a Telegram user by their ID.

        The button generates a ``tg://user?id=<user_id>`` link via
        :class:`~telekit.types.ContactButton`, allowing you to mention a user
        without knowing their username.

        :param text: Label displayed on the button.
        :type text: :class:`str`
        :param user_id: Telegram user ID to mention.
        :type user_id: :class:`str` | :class:`int`
        :param style: Visual style of the button. Accepts a :class:`~telekit.types.ButtonStyle`
            enum value or its string equivalent: ``"danger"`` (red), ``"success"`` (green),
            ``"primary"`` (blue). Defaults to the client-specific style if omitted.
        :type style: :class:`~telekit.types.ButtonStyle` | :class:`str` | ``None``
        :param when: If ``False`` (or any falsy value), the button is skipped and not added
            to the keyboard. Useful for conditional layouts.
        :type when: :class:`bool` | :class:`int`
        :param kwargs: Additional keyword arguments forwarded to
            :class:`~telekit.types.InlineKeyboardButton`.
        :returns: The current builder instance, for method chaining.
        :rtype: :class:`Self`
        """
        if not when:
            return self
        
        self._current.append((text, ContactButton(user_id, style=style, **kwargs)))
        self._maybe_row()
        return self

    def add_user_link(
        self,
        text: str,
        username: str,
        message: str | None = None,
        *,
        style: Literal["danger", "success", "primary"] | None | ButtonStyle = None,
        when: bool | int = True,
        **kwargs
    ):
        """
        Adds a button that opens a Telegram user profile by username.

        The button generates a ``https://t.me/<username>`` link via
        :class:`~telekit.types.UserLinkButton`. Optionally pre-fills
        the chat input with ``message``.

        :param text: Label displayed on the button.
        :type text: :class:`str`
        :param username: Telegram username, with or without a leading ``@``.
        :type username: :class:`str`
        :param message: Optional message text to pre-fill in the chat input.
        :type message: :class:`str` | ``None``
        :param style: Visual style of the button. Accepts a :class:`~telekit.types.ButtonStyle`
            enum value or its string equivalent: ``"danger"`` (red), ``"success"`` (green),
            ``"primary"`` (blue). Defaults to the app-specific style if omitted.
        :type style: :class:`~telekit.types.ButtonStyle` | :class:`str` | ``None``
        :param when: If ``False`` (or any falsy value), the button is skipped and not added
            to the keyboard. Useful for conditional layouts.
        :type when: :class:`bool` | :class:`int`
        :param kwargs: Additional keyword arguments forwarded to
            :class:`~telekit.types.InlineKeyboardButton`.
        :returns: The current builder instance, for method chaining.
        :rtype: :class:`Self`
        """
        if not when:
            return self
        self._current.append((text, UserLinkButton(username, message, style=style, **kwargs)))
        self._maybe_row()
        return self

    def add_bot_link(
            self,
            text: str,
            botname: str,
            start: str | None = None,
            *,
            style: Literal["danger", "success", "primary"] | None | ButtonStyle = None,
            when: bool | int = True,
            **kwargs
        ):
        """
        Adds a button that opens a Telegram bot by username.

        The button generates a ``https://t.me/<botname>`` link via
        :class:`~telekit.types.BotLinkButton`. Optionally appends
        a deep-link payload via ``?start=``.

        :param text: Label displayed on the button.
        :type text: :class:`str`
        :param botname: Bot username, with or without a leading ``@``.
        :type botname: :class:`str`
        :param start: Optional deep-link payload passed as ``?start=``.
            Useful for referral links or onboarding flows.
        :type start: :class:`str` | ``None``
        :param style: Visual style of the button. Accepts a :class:`~telekit.types.ButtonStyle`
            enum value or its string equivalent: ``"danger"`` (red), ``"success"`` (green),
            ``"primary"`` (blue). Defaults to the app-specific style if omitted.
        :type style: :class:`~telekit.types.ButtonStyle` | :class:`str` | ``None``
        :param when: If ``False`` (or any falsy value), the button is skipped and not added
            to the keyboard. Useful for conditional layouts.
        :type when: :class:`bool` | :class:`int`
        :param kwargs: Additional keyword arguments forwarded to
            :class:`~telekit.types.InlineKeyboardButton`.
        :returns: The current builder instance, for method chaining.
        :rtype: :class:`Self`
        """
        if not when:
            return self
        self._current.append((text, BotLinkButton(botname, start, style=style, **kwargs)))
        self._maybe_row()
        return self

    def add_webapp(
        self,
        text: str,
        url: str,
        *,
        style: Literal["danger", "success", "primary"] | None | ButtonStyle = None,
        when: bool | int = True,
        **kwargs
    ):
        """
        Adds a Web App button that opens an HTTPS Telegram mini-app when pressed.

        :param text: The label displayed on the button.
        :type text: `str`

        :param url: An HTTPS URL of a Web App to be opened.
        :type url: `str`

        :param style: Style of the button. Must be one of `telekit.types.ButtonStyle.DANGER` (red),
              `*.SUCCESS` (green) or `*.PRIMARY` (blue).
              You can also pass these as string values: "danger", "success", "primary".
              If omitted, an client-specific default style is used.
        :type style: `str`

        :param when: If `False`, the button is not added.
        :type when: `bool`

        :param kwargs: Additional keyword arguments passed directly to `InlineKeyboardButton`.
        :type kwargs: `Any`
        """
        if not when:
            return self
        self._current.append((text, WebAppButton(url, style=style, **kwargs)))
        self._maybe_row()
        return self

    def add_suggest(
        self,
        text: str,
        suggestion: str,
        *,
        style: Literal["danger", "success", "primary"] | None | ButtonStyle = None,
        strict: bool = True,
        when: bool | int = True,
        **kwargs
    ):
        """
        Adds a suggestion button that simulates the user sending a message when pressed.

        :param text: The label displayed on the button.
        :type text: `str`

        :param suggestion: The suggestion text; 1-64 bytes.
        :type suggestion: `str`

        :param style: Style of the button. Must be one of `telekit.types.ButtonStyle.DANGER` (red),
              `*.SUCCESS` (green) or `*.PRIMARY` (blue).
              You can also pass these as string values: "danger", "success", "primary".
              If omitted, an client-specific default style is used.
        :type style: `str`

        :param strict: If `True`, raises an error when the suggestion exceeds Telegram's 64-byte limit.
        :type strict: `bool`

        :param when: If `False`, the button is not added.
        :type when: `bool`

        :param kwargs: Additional keyword arguments passed directly to `InlineKeyboardButton`.
        :type kwargs: `Any`
        """
        if not when:
            return self
        self._current.append((text, SuggestButton(suggestion, style=style, strict=strict, **kwargs)))
        self._maybe_row()
        return self

    def add_copy(
        self,
        text: str,
        copy_text: str,
        *,
        style: Literal["danger", "success", "primary"] | None | ButtonStyle = None,
        strict: bool = True,
        when: bool | int = True,
        **kwargs
    ):
        """
        Adds a button that copies the specified text to the clipboard when pressed.

        :param text: The label displayed on the button.
        :type text: `str`

        :param copy_text: The text to be copied to the clipboard; 1-256 characters.
        :type copy_text: `str`

        :param style: Style of the button. Must be one of `telekit.types.ButtonStyle.DANGER` (red),
              `*.SUCCESS` (green) or `*.PRIMARY` (blue).
              You can also pass these as string values: "danger", "success", "primary".
              If omitted, an client-specific default style is used.
        :type style: `str`

        :param strict: If `True`, raises an error when the text exceeds Telegram's 256-character limit.
        :type strict: `bool`

        :param when: If `False`, the button is not added.
        :type when: `bool`

        :param kwargs: Additional keyword arguments passed directly to `InlineKeyboardButton`.
        :type kwargs: `Any`
        """
        if not when:
            return self
        self._current.append((text, CopyTextButton(copy_text, style=style, strict=strict, **kwargs)))
        self._maybe_row()
        return self

    def add_static(
        self,
        text: str,
        *,
        style: Literal["danger", "success", "primary"] | None | ButtonStyle = None,
        when: bool | int = True,
        **kwargs
    ):
        """
        Adds a static button with no action attached.

        :param text: The label displayed on the button.
        :type text: `str`

        :param style: Style of the button. Must be one of `telekit.types.ButtonStyle.DANGER` (red),
              `*.SUCCESS` (green) or `*.PRIMARY` (blue).
              You can also pass these as string values: "danger", "success", "primary".
              If omitted, an client-specific default style is used.
        :type style: `str`

        :param when: If `False`, the button is not added.
        :type when: `bool`

        :param kwargs: Additional keyword arguments passed directly to `InlineKeyboardButton`.
        :type kwargs: `Any`
        """
        if not when:
            return self
        self._current.append((text, StaticButton(style=style, **kwargs)))
        self._maybe_row()
        return self

    def add_alert(
        self,
        text: str,
        alert_text: str | None = None,
        *,
        persistent: bool = True,
        style: Literal["danger", "success", "primary"] | None | ButtonStyle = None,
        when: bool | int = True,
        **kwargs
    ):
        """
        Adds a button that shows a popup alert dialog when pressed and terminates the chain.

        :param text: The label displayed on the button.
        :type text: `str`

        :param alert_text: Text to display in the alert popup.
        :type alert_text: `str | None`

        :param persistent: If `True`, the chain is not finalized and other buttons remain active.
        :type persistent: `bool`

        :param style: Style of the button. Must be one of `telekit.types.ButtonStyle.DANGER` (red),
              `*.SUCCESS` (green) or `*.PRIMARY` (blue).
              You can also pass these as string values: "danger", "success", "primary".
              If omitted, an client-specific default style is used.
        :type style: `str`

        :param when: If `False`, the button is not added.
        :type when: `bool`

        :param kwargs: Additional keyword arguments passed directly to `InlineKeyboardButton`.
        :type kwargs: `Any`
        """
        if not when:
            return self
        self._current.append((text, AlertButton(alert_text, persistent=persistent, style=style, **kwargs)))
        self._maybe_row()
        return self

    def add_notification(
        self,
        text: str,
        notification_text: str | None = None,
        *,
        persistent: bool = True,
        style: Literal["danger", "success", "primary"] | None | ButtonStyle = None,
        when: bool | int = True,
        **kwargs
    ):
        """
        Adds a button that shows a brief notification at the top of the chat when pressed and terminates the chain.

        :param text: The label displayed on the button.
        :type text: `str`

        :param notification_text: Text to display in the notification.
        :type notification_text: `str | None`

        :param persistent: If `True`, the chain is not finalized and other buttons remain active.
        :type persistent: `bool`

        :param style: Style of the button. Must be one of `telekit.types.ButtonStyle.DANGER` (red),
              `*.SUCCESS` (green) or `*.PRIMARY` (blue).
              You can also pass these as string values: "danger", "success", "primary".
              If omitted, an client-specific default style is used.
        :type style: `str`

        :param when: If `False`, the button is not added.
        :type when: `bool`

        :param kwargs: Additional keyword arguments passed directly to `InlineKeyboardButton`.
        :type kwargs: `Any`
        """
        if not when:
            return self
        self._current.append((text, NotificationButton(notification_text, persistent=persistent, style=style, **kwargs)))
        self._maybe_row()
        return self

    def add_invoke(
        self,
        text: str,
        obj: Any,
        invoke: str,
        pass_args: tuple | list | None = None,
        pass_kwargs: dict[str, Any] | None = None,
        *,
        answer_text: str | None = None,
        answer_as_alert: bool = True,
        style: Literal["danger", "success", "primary"] | None | ButtonStyle = None,
        when: bool | int = True,
        **kwargs
    ):
        """
        Adds a button that calls a named method on a given object when pressed.

        :param text: The label displayed on the button.
        :type text: `str`

        :param obj: The object on which the method will be called.
        :type obj: `Any`

        :param invoke: Name of the method to call on `obj`.
        :type invoke: `str`

        :param pass_args: Positional arguments to pass into the method.
        :type pass_args: `tuple | list | None`

        :param pass_kwargs: Keyword arguments to pass into the method.
        :type pass_kwargs: `dict[str, Any] | None`

        :param answer_text: Optional text to send as an answer to the callback query.
        :type answer_text: `str | None`

        :param answer_as_alert: If `True`, the answer is shown as a popup alert.
            If `False`, it appears as a notification at the top of the chat.
        :type answer_as_alert: `bool`

        :param style: Style of the button. Must be one of `telekit.types.ButtonStyle.DANGER` (red),
              `*.SUCCESS` (green) or `*.PRIMARY` (blue).
              You can also pass these as string values: "danger", "success", "primary".
              If omitted, an client-specific default style is used.
        :type style: `str`

        :param when: If `False`, the button is not added.
        :type when: `bool`

        :param kwargs: Additional keyword arguments passed directly to `InlineKeyboardButton`.
        :type kwargs: `Any`
        """
        if not when:
            return self
        button = InvokeButton(
            obj, invoke,
            pass_args, pass_kwargs,
            answer_text=answer_text,
            answer_as_alert=answer_as_alert,
            style=style,
            **kwargs
        )
        self._current.append((text, button))
        self._maybe_row()
        return self
    
    def extend(
        self,
        buttons: dict[str, InlineButton | None] | list[str],
        *,
        width: int | bool = False,
        when: bool | int = True,
    ) -> "InlineKeyboard":
        """
        Adds multiple buttons at once from a dict or list.

        :param buttons: A dict mapping button labels to :class:`InlineButton` instances,
            or a list of labels (each rendered as a :class:`StaticButton`).
        :type buttons: `dict[str, InlineButton | None] | list[str]`

        :param width: Controls how the added buttons are split into rows.
            ``False`` / ``0`` places all buttons in a single row. 
            ``True`` / ``1`` places each button on its own row,
            same as wrapping with :meth:`column` / :meth:`column_end`.
            Any value ``n >= 2`` splits the buttons into rows of ``n`` buttons
            each, same as :meth:`grid` / :meth:`grid_end`.
            The previous grid width is restored after the call.
        :type width: `int | bool`

        :param when: If `False`, the buttons are not added.
        :type when: `bool`

        Example::

            InlineKeyboard()
                .extend({"Option A": btn_a, "Option B": btn_b}, width=1)
                .add_callback("« Back", self.handle)
        """
        if not when:
            return self

        _saved_width: int = self._grid_width
        self.grid(int(width))

        if isinstance(buttons, dict):
            for text, button in buttons.items():
                self.add(text, button)
        else:
            for text in buttons:
                self.add(text, None)

        # Restore directly: no need to call grid_end() separately,
        # because the last add() already flushed _current via _maybe_row().
        self._grid_width = _saved_width
        return self
    
    def extend_rows(self, *rows: list[tuple[str, InlineButton]], when: bool | int = True,) -> "InlineKeyboard":
        """
        Adds one or more fully-defined rows to the keyboard.

        Each row must be provided in the same format: a list of ``(text, button)`` tuples.

        :param rows: Rows to append to the keyboard.
        :type rows: `list[tuple[str, InlineButton]]`

        :param when: If `False`, the rows are not added.
        :type when: `bool`

        Example::

            InlineKeyboard()
                .extend_rows(
                    [ ("Option A", btn_a), ("Option B", btn_b) ],
                    [           ("« Back", back_btn)           ],
                )
        """
        if not when:
            return self
        
        self.row()
        self._rows.extend(rows)

        return self
