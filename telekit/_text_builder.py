from dataclasses import dataclass
from typing import Any, Literal, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from string.templatelib import Template  # pyright: ignore[reportMissingImports]

from .styles import (
    TextEntity, Group,
    Bold, Italic, Underline, Strikethrough,
    Code, Language, Python, Spoiler, Quote,
    Escape, Raw, Link, Mention, UserLink, BotLink,
    Stack,
)


_SepType = Union[str, "TextEntity", "Template"]


@dataclass
class _CondFrame:
    active: bool
    type: Literal["if", "else"]


class TextBuilder(TextEntity):
    """
    Fluent builder for composing messages from multiple
    ``TextEntity`` / string pieces.

    Works just like ``InlineKeyboard`` does for buttons: call chained
    ``add_*`` methods, then pass the builder directly to ``sender.set_message()``
    (or ``set_text()``), because ``TextBuilder`` itself **is** a ``TextEntity``.

    :param sep: Separator inserted between every two adjacent items that were
        added to the builder.  Defaults to ``""`` (no separator).

    Grid mode
    ---------
    ``grid(width)`` / ``end_grid()`` automatically insert a separator after
    every *width* items, useful when you want N entities per "row"
    (e.g. ``sep="\\n"`` with ``grid(1)`` gives one entity per line).

    ``stack()`` is a convenience alias for ``grid(1)`` — one item per line.
    ``end_stack()`` is an alias for ``end_grid()``.

    Conditional blocks
    ------------------
    ``if_(cond)`` opens a block: all ``add_*`` / ``newln`` / ``spacer`` calls
    inside are skipped when *cond* is falsy.  Conditions nest — every frame
    on the stack must be truthy for items to be added.

    ``else_()`` flips the innermost condition (else-branch).
    ``endif()`` closes the block.

    Examples::

        TextBuilder(sep="\\n")
            .add_bold("Hello")
            .add("World")
            .render("html")
        # "<b>Hello</b>\\nWorld"

        sender.set_message(
            TextBuilder()
                .if_(self.click_count)
                    .add_group("You clicked", Bold(self.click_count), "times.", sep=" ", when=not show_tip)
                    .add_group("Telekit says", Bold("#", self.click_count), sep=" ", when=show_tip)
                    .newln()
                    .add_quote(GUIDELINES[self.click_count - 3], when=show_tip)
                .endif()
                .add("Click the button below to start interacting", when=not self.click_count)
        )

        # Nested conditions + else:
        TextBuilder()
            .if_(is_admin)
                .add_bold("Admin panel")
                .if_(has_alerts)
                    .add_italic("Alerts pending!")
                .endif()
            .else_()          # else: not is_admin
                .add("Guest view")
            .endif()

    `Documentation <https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md>`_ · on GitHub
    """

    def __init__(self, sep: _SepType = ""):
        super().__init__(escape=True, sep=sep)

        self._items: list[TextEntity | str] = []
        self._builder_sep: _SepType = sep
        self._grid_width: int = 0
        self._grid_counter: int = 0
        self._when_stack: list[_CondFrame] = []

    # ------------------------------------------------------------------
    # TextEntity integration — override rendering to use _items
    # ------------------------------------------------------------------

    def _render_content(self, parse_mode: Literal["html", "markdown"] | None) -> str:
        sep: str = self._render_item(self._builder_sep, parse_mode)
        parts: list[str] = []

        for item in self._items:
            if isinstance(item, TextEntity):
                rendered = item.render(parse_mode)
            else:
                # raw separator/newline strings injected by newln()/spacer()
                rendered = str(item)

            parts.append(rendered)

        return sep.join(parts)

    def render(self, parse_mode: Literal["html", "markdown"] | None) -> str:
        if self._when_stack:
            depth = len(self._when_stack)
            raise RuntimeError(
                f"{depth} unclosed if_() block(s) detected at render time — "
                f"each if_() must be closed with a matching endif()."
            )
        return super().render(parse_mode)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _active(self) -> bool:
        """Return True when every _CondFrame on the stack is active."""
        return all(frame.active for frame in self._when_stack)

    def _push(self, entity: TextEntity, when: Any) -> "TextBuilder":
        """Append *entity* respecting both the local *when* and the when-stack."""
        if not when or not self._active():
            return self

        self._items.append(entity)

        if self._grid_width:
            self._grid_counter += 1
            if self._grid_counter >= self._grid_width:
                self._grid_counter = 0
                self._items.append(_GridBreak(self._builder_sep))

        return self

    # ------------------------------------------------------------------
    # Grid / stack control
    # ------------------------------------------------------------------

    def grid(self, width: int) -> "TextBuilder":
        """
        Enable grid mode: after every *width* items a separator is automatically
        inserted.  Use ``end_grid()`` to leave grid mode.

        :param width: Number of items per "row". ``0`` disables grid mode.
        """
        if width < 0:
            raise ValueError("width must be >= 0")
        self._grid_width = width
        self._grid_counter = 0
        return self

    def end_grid(self) -> "TextBuilder":
        """Disable grid mode."""
        self._grid_width = 0
        self._grid_counter = 0
        return self

    def stack(self) -> "TextBuilder":
        """
        Convenience alias for ``grid(1)`` — every item goes on its own line
        (separated by the builder's *sep*).
        """
        return self.grid(1)

    def end_stack(self) -> "TextBuilder":
        """Alias for ``end_grid()``."""
        return self.end_grid()

    # ------------------------------------------------------------------
    # Conditional blocks — if_() / else_() / endif()
    # ------------------------------------------------------------------

    def if_(self, condition: Any) -> "TextBuilder":
        """
        Open a conditional block: every ``add_*`` / ``newln`` / ``spacer``
        call inside the block is skipped unless *all* active conditions on
        the stack are truthy.

        Conditions nest: an inner ``if_()`` requires **both** the outer
        and the inner condition to be truthy.

        Close the block with :meth:`endif`.  Switch to the else-branch
        with :meth:`else_` (which flips the innermost condition).

        :param condition: Any truthy/falsy value.

        Example::

            TextBuilder()
                .if_(is_admin)
                    .add_bold("Admin panel")
                    .if_(has_alerts)
                        .add_italic("You have alerts!")
                    .endif()
                .else_()          # else: not is_admin
                    .add("Guest view")
                .endif()
        """
        self._when_stack.append(_CondFrame(active=bool(condition), type="if"))
        return self

    def else_(self) -> "TextBuilder":
        """
        Switch to the **else**-branch of the innermost :meth:`if_` block.

        Flips the active state of the innermost frame so that everything
        that follows (until :meth:`endif`) is rendered only when the
        original condition was *falsy*.

        Raises ``RuntimeError`` if the stack is empty or if ``else_()`` was
        already called for the current block.
        """
        if not self._when_stack:
            raise RuntimeError(
                "else_() called without a matching if_() — condition stack is empty."
            )
        frame = self._when_stack[-1]
        if frame.type == "else":
            raise RuntimeError(
                "else_() called twice for the same if_() block — "
                "only one else_() per if_() is allowed."
            )
        frame.active = not frame.active
        frame.type = "else"
        return self

    def endif(self) -> "TextBuilder":
        """
        Close the innermost :meth:`if_` / :meth:`else_` block.

        Raises ``RuntimeError`` if the stack is empty.
        """
        if not self._when_stack:
            raise RuntimeError(
                "endif() called without a matching if_() — condition stack is empty."
            )
        self._when_stack.pop()
        return self

    # ------------------------------------------------------------------
    # Spacer helpers
    # ------------------------------------------------------------------

    def newln(self, n: int = 1, when: bool | Any = True) -> "TextBuilder":
        """
        Insert ``n`` newline characters (``\\n``) as a hard separator,
        independent of the builder's *sep*.

        Respects the active ``if_()`` stack — no newline is inserted if
        the current block is inactive.

        Defaults to a single ``\\n``.
        """
        if when and self._active():
            self._items.append(_RawStr("\n" * n))
        return self

    def spacer(self, n: int = 2, when: bool | Any = True) -> "TextBuilder":
        """
        Insert ``n`` newline characters as a hard separator (default 2 = blank line).
        Convenience alias for ``newln(2)``.
        """
        return self.newln(n, when)

    # ------------------------------------------------------------------
    # Generic add
    # ------------------------------------------------------------------

    def add(
        self,
        *content: Union[str, TextEntity],
        escape: bool = True,
        sep: _SepType = "",
        when: Any = True,
    ) -> "TextBuilder":
        """
        Add one or more strings / ``TextEntity`` objects as a ``Group``.

        :param content: Items to group together.
        :param escape: Whether to escape special characters in plain strings.
        :param sep: Separator between items inside this group.
        :param when: If falsy, skip this item entirely.
        """
        return self._push(Group(*content, escape=escape, sep=sep), when)

    # ------------------------------------------------------------------
    # Style shortcuts — add_<style>
    # ------------------------------------------------------------------

    def add_group(
        self,
        *content: Union[str, TextEntity],
        escape: bool = True,
        sep: _SepType = "",
        when: Any = True,
    ) -> "TextBuilder":
        """Add a ``Group`` — identical to :meth:`add`."""
        return self.add(*content, escape=escape, sep=sep, when=when)

    def add_bold(
        self,
        *content: Union[str, TextEntity],
        escape: bool = True,
        sep: _SepType = "",
        when: Any = True,
    ) -> "TextBuilder":
        """Add a :class:`Bold` entity."""
        return self._push(Bold(*content, escape=escape, sep=sep), when)

    def add_italic(
        self,
        *content: Union[str, TextEntity],
        escape: bool = True,
        sep: _SepType = "",
        when: Any = True,
    ) -> "TextBuilder":
        """Add an :class:`Italic` entity."""
        return self._push(Italic(*content, escape=escape, sep=sep), when)

    def add_underline(
        self,
        *content: Union[str, TextEntity],
        escape: bool = True,
        sep: _SepType = "",
        when: Any = True,
    ) -> "TextBuilder":
        """Add an :class:`Underline` entity."""
        return self._push(Underline(*content, escape=escape, sep=sep), when)

    def add_strikethrough(
        self,
        *content: Union[str, TextEntity],
        escape: bool = True,
        sep: _SepType = "",
        when: Any = True,
    ) -> "TextBuilder":
        """Add a :class:`Strikethrough` entity."""
        return self._push(Strikethrough(*content, escape=escape, sep=sep), when)

    def add_code(
        self,
        *content: Union[str, TextEntity],
        escape: bool = True,
        sep: _SepType = "",
        when: Any = True,
    ) -> "TextBuilder":
        """Add a :class:`Code` (inline monospace) entity."""
        return self._push(Code(*content, escape=escape, sep=sep), when)

    def add_language(
        self,
        *content: Union[str, TextEntity],
        lang: str,
        escape: bool = True,
        sep: _SepType = "",
        when: Any = True,
    ) -> "TextBuilder":
        """Add a :class:`Language` code block entity."""
        return self._push(Language(*content, lang=lang, escape=escape, sep=sep), when)

    def add_python(
        self,
        *content: Union[str, TextEntity],
        escape: bool = True,
        sep: _SepType = "",
        when: Any = True,
    ) -> "TextBuilder":
        """Add a :class:`Python` code block entity."""
        return self._push(Python(*content, escape=escape, sep=sep), when)

    def add_spoiler(
        self,
        *content: Union[str, TextEntity],
        escape: bool = True,
        sep: _SepType = "",
        when: Any = True,
    ) -> "TextBuilder":
        """Add a :class:`Spoiler` entity."""
        return self._push(Spoiler(*content, escape=escape, sep=sep), when)

    def add_quote(
        self,
        *content: Union[str, TextEntity],
        expandable: bool = False,
        end: str = "\n",
        escape: bool = True,
        sep: _SepType = "",
        when: Any = True,
    ) -> "TextBuilder":
        """Add a :class:`Quote` (blockquote) entity."""
        return self._push(
            Quote(*content, expandable=expandable, end=end, escape=escape, sep=sep),
            when,
        )

    def add_escape(
        self,
        *content: Union[str, TextEntity],
        sep: _SepType = "",
        when: Any = True,
    ) -> "TextBuilder":
        """Add an :class:`Escape` entity (force-escape special chars)."""
        return self._push(Escape(*content, sep=sep), when)

    def add_raw(
        self,
        *content: Union[str, TextEntity],
        sep: _SepType = "",
        when: Any = True,
    ) -> "TextBuilder":
        """Add a :class:`Raw` entity (no escaping)."""
        return self._push(Raw(*content, sep=sep), when)

    def add_link(
        self,
        *content: Union[str, TextEntity],
        url: str,
        escape: bool = True,
        sep: _SepType = "",
        when: Any = True,
    ) -> "TextBuilder":
        """Add a :class:`Link` entity."""
        return self._push(Link(*content, url=url, escape=escape, sep=sep), when)

    def add_mention(
        self,
        *content: Union[str, TextEntity],
        user_id: int | str,
        escape: bool = True,
        sep: _SepType = "",
        when: Any = True,
    ) -> "TextBuilder":
        """Add a :class:`Mention` entity (link by user ID)."""
        return self._push(
            Mention(*content, user_id=user_id, escape=escape, sep=sep), when
        )

    def add_user_link(
        self,
        *content: Union[str, TextEntity],
        username: str,
        text: str | None = None,
        escape: bool = True,
        sep: _SepType = "",
        when: Any = True,
    ) -> "TextBuilder":
        """Add a :class:`UserLink` entity (link by username)."""
        return self._push(
            UserLink(*content, username=username, text=text, escape=escape, sep=sep),
            when,
        )

    def add_bot_link(
        self,
        *content: Union[str, TextEntity],
        username: str,
        start: str | None = None,
        escape: bool = True,
        sep: _SepType = "",
        when: Any = True,
    ) -> "TextBuilder":
        """Add a :class:`BotLink` entity (bot deep link)."""
        return self._push(
            BotLink(*content, username=username, start=start, escape=escape, sep=sep),
            when,
        )

    def add_stack(
        self,
        *content: Union[str, TextEntity],
        start: str = "{{index}}. ",
        sep: _SepType = "\n",
        end: _SepType = "",
        escape: bool = True,
        when: Any = True,
    ) -> "TextBuilder":
        """
        Add a :class:`Stack` entity (numbered / bulleted list).

        Note: this adds a *single* Stack entity. Use ``stack()`` / ``end_stack()``
        to put separate builder items one-per-line.
        """
        return self._push(
            Stack(*content, start=start, sep=sep, end=end, escape=escape), when
        )


# ---------------------------------------------------------------------------
# Internal sentinel types — not part of public API
# ---------------------------------------------------------------------------

class _RawStr(TextEntity):
    """A fixed string injected directly into the builder output (e.g. newlines)."""

    def __init__(self, value: str):
        super().__init__(escape=False)
        self._value = value

    def _render_content(self, parse_mode: Any) -> str:  # type: ignore[override]
        return self._value


class _GridBreak(_RawStr):
    """
    Separator inserted automatically by grid mode.
    Rendered as the builder's *sep* string (already resolved at push time).
    """

    def __init__(self, sep: _SepType):
        if isinstance(sep, str):
            value = sep
        elif isinstance(sep, TextEntity):
            value = sep.render_html()
        else:
            value = str(sep)
        super().__init__(value)