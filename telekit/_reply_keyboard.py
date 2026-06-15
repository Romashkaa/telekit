from typing import Any

from telebot.types import ReplyKeyboardMarkup

from telekit.reply_buttons import (
    ReplyButton, TextButton, ContactButton, LocationButton,
    PollButton, WebAppReplyButton, RequestUserButton, RequestChatButton,
)

__all__ = [
    "ReplyKeyboard",
]

class ReplyKeyboard:
    """
    A fluent builder for Telegram reply keyboards.

    Produces a :class:`telebot.types.ReplyKeyboardMarkup` via :meth:`build`.
    Supports all button types available in the Telegram Bot API for reply keyboards,
    as well as row/column layout helpers and bulk-add methods identical in spirit
    to ``InlineKeyboard``.

    Basic usage::

        markup = (
            ReplyKeyboard(resize_keyboard=True)
                .add_contact("📱 Share phone")
                .add_location("📍 My location")
            .row()
                .add_text("Option A")
                .add_text("Option B")
            .build()
        )
        bot.send_message(chat_id, "Choose:", reply_markup=markup)

    :param keyboard: Pre-built rows of ``(text, ReplyButton)`` tuples to seed
        the builder with. Useful for composing keyboards programmatically.
    :type keyboard: list[list[tuple[str, ReplyButton]]] or None
    :param resize_keyboard: If ``True``, the keyboard is resized to fit the buttons.
        Defaults to ``True``.
    :type resize_keyboard: bool
    :param one_time_keyboard: If ``True``, the keyboard is hidden after the first use.
        Defaults to ``False``.
    :type one_time_keyboard: bool
    :param input_field_placeholder: Placeholder text shown in the input field
        while the keyboard is active. Up to 64 characters.
    :type input_field_placeholder: str or None
    :param selective: If ``True``, the keyboard is shown only to mentioned users
        or the original message sender. Defaults to ``False``.
    :type selective: bool
    :param is_persistent: If ``True``, the keyboard is always shown and is not
        collapsed to a small icon. Defaults to ``False``.
    :type is_persistent: bool
    """

    def __init__(
        self,
        keyboard: list[list[tuple[str, ReplyButton]]] | None = None,
        *,
        resize_keyboard: bool = True,
        one_time_keyboard: bool = False,
        input_field_placeholder: str | None = None,
        selective: bool = False,
        is_persistent: bool = False,
    ) -> None:
        self._rows: list[list[tuple[str, ReplyButton]]] = []
        if keyboard is not None:
            self._rows.extend(keyboard)

        self._current: list[tuple[str, ReplyButton]] = []
        self._grid_width: int = 0

        self._resize_keyboard = resize_keyboard
        self._one_time_keyboard = one_time_keyboard
        self._input_field_placeholder = input_field_placeholder
        self._selective = selective
        self._is_persistent = is_persistent

    # ── Layout helpers ────────────────────────────────────────────────────────

    def row(self, *, when: bool = True) -> "ReplyKeyboard":
        """
        Finalize the current row and start a new one.

        Calling this method is optional at the end of the chain — :meth:`build`
        flushes any pending row automatically.

        :param when: If ``False``, the row is not finalized and the builder
            is returned unchanged. Useful for conditional layouts.
        :type when: bool
        :rtype: :class:`ReplyKeyboard`
        """
        if not when:
            return self
        if self._current:
            self._rows.append(self._current)
            self._current = []
        return self

    def grid(self, width: int = 1) -> "ReplyKeyboard":
        """
        Enable grid mode: buttons added after this call will be
        automatically split into rows of ``width`` buttons each.

        Use together with :meth:`grid_end` to wrap a block of buttons.

        :param width: Number of buttons per row. ``0`` disables grid mode
            (no automatic row breaks).
        :type width: int
        :rtype: :class:`ReplyKeyboard`

        Example::

            ReplyKeyboard()
                .grid(width=3)
                    .add_text("1")
                    .add_text("2")
                    .add_text("3")
                    .add_text("4")
                    .add_text("5")
                .grid_end()

        This produces rows of [1, 2, 3], [4, 5].
        """
        if width < 0:
            raise ValueError("width must be >= 0")
        self._grid_width = width
        self.row()
        return self

    def grid_end(self) -> "ReplyKeyboard":
        """
        Disable grid mode and finalize the current row.

        Calls :meth:`row` automatically so the next buttons added
        outside the grid block start on a fresh row.

        :rtype: :class:`ReplyKeyboard`
        """
        self._grid_width = 0
        self.row()
        return self

    def column(self) -> "ReplyKeyboard":
        """
        Enable column mode: every button added after this call
        will automatically be placed on its own row.

        Alias for :meth:`grid` with ``width=1``.

        Use together with :meth:`column_end` to wrap a block of buttons.

        Example::

            ReplyKeyboard()
                .column()
                    .add_text("First")
                    .add_text("Second")
                    .add_text("Third")
                .column_end()

        :rtype: :class:`ReplyKeyboard`
        """
        return self.grid(1)

    def column_end(self) -> "ReplyKeyboard":
        """
        Disable column mode and finalize the current row.

        Alias for :meth:`grid_end`.

        :rtype: :class:`ReplyKeyboard`
        """
        return self.grid_end()

    def _grid_count(self) -> int:
        """
        Returns the number of buttons currently in the unfinalized row.
        """
        return len(self._current)

    def _maybe_row(self) -> None:
        """Flush the current row when the grid width is reached."""
        if self._grid_width and self._grid_count() >= self._grid_width:
            self.row()

    # ── Generic add ───────────────────────────────────────────────────────────

    def add(
        self,
        text: str,
        reply_button: ReplyButton | None = None,
        *,
        when: bool = True,
    ) -> "ReplyKeyboard":
        """
        Add a button to the current row.

        This is the low-level method used internally by all typed ``add_*``
        helpers. Prefer those for clarity; use this only when passing a button
        instance directly.

        :param text: Label displayed on the button.
        :type text: str
        :param reply_button: Button descriptor. Defaults to :class:`TextButton`
            when ``None``.
        :type reply_button: :class:`ReplyButton` or None
        :param when: If ``False``, the button is skipped. Useful for conditional
            layouts.
        :type when: bool
        :rtype: :class:`ReplyKeyboard`
        """
        if not when:
            return self
        self._current.append(
            (text, reply_button if reply_button is not None else TextButton())
        )
        self._maybe_row()
        return self

    # ── Typed add helpers ─────────────────────────────────────────────────────

    def add_text(self, text: str, *, when: bool = True) -> "ReplyKeyboard":
        """
        Add a plain text button.

        When pressed, the button label is sent as a regular user message.

        :param text: Label displayed on the button.
        :type text: str
        :param when: If ``False``, the button is skipped.
        :type when: bool
        :rtype: :class:`ReplyKeyboard`
        """
        return self.add(text, TextButton(), when=when)

    def add_contact(self, text: str, *, when: bool = True) -> "ReplyKeyboard":
        """
        Add a contact-request button.

        Telegram prompts the user to share their phone number.
        Only available in private chats.

        :param text: Label displayed on the button.
        :type text: str
        :param when: If ``False``, the button is skipped.
        :type when: bool
        :rtype: :class:`ReplyKeyboard`
        """
        return self.add(text, ContactButton(), when=when)

    def add_location(self, text: str, *, when: bool = True) -> "ReplyKeyboard":
        """
        Add a location-request button.

        Telegram prompts the user to share their current geolocation.
        Only available in private chats.

        :param text: Label displayed on the button.
        :type text: str
        :param when: If ``False``, the button is skipped.
        :type when: bool
        :rtype: :class:`ReplyKeyboard`
        """
        return self.add(text, LocationButton(), when=when)

    def add_poll(
        self,
        text: str,
        poll_type: str | None = None,
        *,
        when: bool = True,
    ) -> "ReplyKeyboard":
        """
        Add a poll-creation button.

        :param text: Label displayed on the button.
        :type text: str
        :param poll_type: Restricts the poll type the user may create.
            Accepted values: ``"quiz"``, ``"regular"``, or ``None`` (any type).
        :type poll_type: str or None
        :param when: If ``False``, the button is skipped.
        :type when: bool
        :rtype: :class:`ReplyKeyboard`
        """
        return self.add(text, PollButton(poll_type=poll_type), when=when)

    def add_webapp(
        self,
        text: str,
        url: str,
        *,
        when: bool = True,
    ) -> "ReplyKeyboard":
        """
        Add a Web App button.

        Opens the specified Telegram Mini App when pressed.

        :param text: Label displayed on the button.
        :type text: str
        :param url: HTTPS URL of the Web App to open.
        :type url: str
        :param when: If ``False``, the button is skipped.
        :type when: bool
        :rtype: :class:`ReplyKeyboard`
        """
        return self.add(text, WebAppReplyButton(url=url), when=when)

    def add_request_user(
        self,
        text: str,
        request_id: int,
        *,
        user_is_bot: bool | None = None,
        user_is_premium: bool | None = None,
        when: bool = True,
    ) -> "ReplyKeyboard":
        """
        Add a user-selection button.

        Telegram opens a dialog that lets the user pick another Telegram user.
        The selected user's ID is sent back via a ``KeyboardButtonRequestUser``
        service message.

        :param text: Label displayed on the button.
        :type text: str
        :param request_id: Signed 32-bit identifier of the request.
            Must be unique within the message.
        :type request_id: int
        :param user_is_bot: Filter by bot status.
            ``True`` — bots only, ``False`` — humans only, ``None`` — no filter.
        :type user_is_bot: bool or None
        :param user_is_premium: Filter by Premium status.
            ``True`` — Premium only, ``False`` — non-Premium only, ``None`` — no filter.
        :type user_is_premium: bool or None
        :param when: If ``False``, the button is skipped.
        :type when: bool
        :rtype: :class:`ReplyKeyboard`
        """
        return self.add(
            text,
            RequestUserButton(
                request_id=request_id,
                user_is_bot=user_is_bot,
                user_is_premium=user_is_premium,
            ),
            when=when,
        )

    def add_request_chat(
        self,
        text: str,
        request_id: int,
        *,
        chat_is_channel: bool = False,
        chat_is_forum: bool | None = None,
        chat_has_username: bool | None = None,
        chat_is_created: bool | None = None,
        user_administrator_rights: Any | None = None,
        bot_administrator_rights: Any | None = None,
        bot_is_member: bool | None = None,
        when: bool = True,
    ) -> "ReplyKeyboard":
        """
        Add a chat-selection button.

        Telegram opens a dialog that lets the user pick a chat.
        The selected chat's ID is sent back via a ``KeyboardButtonRequestChat``
        service message.

        :param text: Label displayed on the button.
        :type text: str
        :param request_id: Signed 32-bit identifier of the request.
            Must be unique within the message.
        :type request_id: int
        :param chat_is_channel: If ``True``, only channels are listed.
            If ``False``, only groups and supergroups are listed.
        :type chat_is_channel: bool
        :param chat_is_forum: If ``True``, only forum supergroups are listed.
        :type chat_is_forum: bool or None
        :param chat_has_username: If ``True``, only public chats are listed.
        :type chat_has_username: bool or None
        :param chat_is_created: If ``True``, only chats created by the user are listed.
        :type chat_is_created: bool or None
        :param user_administrator_rights: Required administrator rights of the
            user in the selected chat.
        :type user_administrator_rights: :class:`telebot.types.ChatAdministratorRights` or None
        :param bot_administrator_rights: Required administrator rights of the
            bot in the selected chat.
        :type bot_administrator_rights: :class:`telebot.types.ChatAdministratorRights` or None
        :param bot_is_member: If ``True``, the bot must already be a member of
            the selected chat.
        :type bot_is_member: bool or None
        :param when: If ``False``, the button is skipped.
        :type when: bool
        :rtype: :class:`ReplyKeyboard`
        """
        return self.add(
            text,
            RequestChatButton(
                request_id=request_id,
                chat_is_channel=chat_is_channel,
                chat_is_forum=chat_is_forum,
                chat_has_username=chat_has_username,
                chat_is_created=chat_is_created,
                user_administrator_rights=user_administrator_rights,
                bot_administrator_rights=bot_administrator_rights,
                bot_is_member=bot_is_member,
            ),
            when=when,
        )

    # ── Bulk helpers ──────────────────────────────────────────────────────────

    def extend(
        self,
        buttons: dict[str, ReplyButton | None] | list[str],
        *,
        width: int | bool = False,
        when: bool = True,
    ) -> "ReplyKeyboard":
        """
        Add multiple buttons at once from a mapping or a list of labels.

        When a ``dict`` is supplied, each key is used as the button label and
        the value as the :class:`ReplyButton` descriptor (``None`` falls back to
        :class:`TextButton`). When a plain ``list`` of strings is supplied,
        every entry becomes a :class:`TextButton`.

        :param buttons: Button definitions — either a ``dict`` of
            ``{label: ReplyButton | None}`` or a ``list[str]`` of labels.
        :type buttons: dict[str, ReplyButton or None] or list[str]
        :param width: Controls how the added buttons are split into rows.
            ``False`` / ``0`` places all buttons in a single row.
            ``True`` / ``1`` places each button on its own row,
            same as wrapping with :meth:`column` / :meth:`column_end`.
            Any value ``n >= 2`` splits the buttons into rows of ``n`` buttons
            each, same as :meth:`grid` / :meth:`grid_end`.
            The previous grid width is restored after the call.
        :type width: int | bool
        :param when: If ``False``, all buttons are skipped.
        :type when: bool
        :rtype: :class:`ReplyKeyboard`

        Example::

            ReplyKeyboard()
                .extend({"📱 Phone": ContactButton(), "📍 Location": LocationButton()})
                .extend(["Quick reply A", "Quick reply B"], width=True)
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
                self.add(text)

        # Restore directly: no need to call grid_end() separately,
        # because the last add() already flushed _current via _maybe_row().
        self._grid_width = _saved_width
        return self

    def extend_rows(
        self,
        *rows: list[tuple[str, ReplyButton]],
        when: bool = True,
    ) -> "ReplyKeyboard":
        """
        Append one or more fully pre-built rows to the keyboard.

        Each row must be a ``list`` of ``(label, ReplyButton)`` tuples,
        matching the internal storage format.

        :param rows: Rows to append. Each row is a
            ``list[tuple[str, ReplyButton]]``.
        :type rows: list[tuple[str, ReplyButton]]
        :param when: If ``False``, the rows are skipped.
        :type when: bool
        :rtype: :class:`ReplyKeyboard`

        Example::

            ReplyKeyboard()
                .extend_rows(
                    [("Option A", TextButton()), ("Option B", TextButton())],
                    [("📱 Phone",  ContactButton())],
                )
        """
        if not when:
            return self
        self.row()
        self._rows.extend(rows)
        return self

    # ── Build ─────────────────────────────────────────────────────────────────

    def _compile(self) -> ReplyKeyboardMarkup:
        """
        Finalize and compile the keyboard into a
        :class:`telebot.types.ReplyKeyboardMarkup`.

        :rtype: :class:`telebot.types.ReplyKeyboardMarkup`
        """
        self.row()
        markup = ReplyKeyboardMarkup(
            resize_keyboard=self._resize_keyboard,
            one_time_keyboard=self._one_time_keyboard,
            input_field_placeholder=self._input_field_placeholder,
            selective=self._selective,
            is_persistent=self._is_persistent,
        )
        for row in self._rows:
            markup.row(*[btn.to_button(text) for text, btn in row])
        return markup