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
"""
Telegram HTML message manipulation with tag-aware indexing and slicing.

This module exposes a single public class, :class:`HTMLText`, which wraps
a Telegram-flavoured HTML string and lets callers treat it as a plain-text
sequence: ``len()``, ``[]`` indexing, and slice notation all operate on
*visible characters only*, with HTML tags automatically reopened / closed
around every sub-sequence.

Supported markup
----------------
All tags recognised by Telegram's HTML parse mode are handled correctly:

* ``<b>``, ``<strong>`` — bold
* ``<i>``, ``<em>`` — italic
* ``<u>``, ``<ins>`` — underline
* ``<s>``, ``<strike>``, ``<del>`` — strikethrough
* ``<code>`` — inline code
* ``<pre language="...">`` — code block
* ``<tg-spoiler>`` — spoiler
* ``<blockquote>`` — block quote (optional *expandable* attribute)
* ``<a href="...">`` — hyperlink / inline mention
* ``<tg-emoji id="...">`` — custom emoji
* HTML character references (``&amp;``, ``&lt;``, numeric, etc.)

Quick start
-----------
::

    >>> from html_text import HTMLText
    >>> msg = HTMLText("<b>Wow!</b>")
    >>> len(msg)
    4
    >>> str(HTMLText("My <b>name is <i>Romashka</i></b>")[3:-2])
    '<b>name is <i>Romash</i></b>'
    >>> [str(c) for c in HTMLText("<b>Hi</b>").stream()]
    ['<b>H</b>', '<b>Hi</b>']
"""

from __future__ import annotations

import re
from typing import Generator, Iterator, Union


# ---------------------------------------------------------------------------
# Internal regular expressions
# ---------------------------------------------------------------------------

#: Matches any HTML tag: opening, closing, or self-closing.
_TAG_RE: re.Pattern[str] = re.compile(
    r'<(?P<close>/)?(?P<name>[a-zA-Z][a-zA-Z0-9\-]*)(?P<attrs>[^>]*)>',
    re.IGNORECASE,
)

#: Matches a single HTML character reference (named, decimal, or hex).
_ENTITY_RE: re.Pattern[str] = re.compile(
    r'&(?:[a-zA-Z]+|#\d+|#x[0-9a-fA-F]+);'
)


# ---------------------------------------------------------------------------
# Window type
# ---------------------------------------------------------------------------

# ``Window`` describes how far a chunk boundary may shift relative to *size*:
#
#   int  n   → shorthand for (n, 0): may be up to n chars SHORTER than size.
#              n must be >= 0.
#   (a, b)   → may be up to *a* chars SHORTER  and up to *b* chars LONGER.
#              Both a and b must be >= 0.
#
# Examples:
#   window=10        → search in [size-10, size]
#   window=(5, 10)   → search in [size-5,  size+10]
#   window=(0, 30)   → search in [size,    size+30]
#   window=0         → always hard-cut at exactly size  (no window)
#   window=None      → greedy: rightmost delimiter anywhere in [1, size]

Window = Union[int, tuple[int, int], None]


def _resolve_window(window: Window, size: int) -> tuple[int, int]:
    """Convert a :data:`Window` value into an absolute ``(win_min, win_max)`` pair.

    :param window: Window specification (see :data:`Window`).
    :param size: Target chunk size in visible characters.
    :returns: ``(win_min, win_max)`` inclusive character counts.
    :raises TypeError: If *window* is not ``int``, ``tuple``, or ``None``.
    :raises ValueError: If tuple elements or the integer are negative.
    """
    if window is None:
        # Greedy: no lower bound, upper bound is size.
        return 1, size

    if isinstance(window, int):
        if window < 0:
            raise ValueError(
                f"window integer must be >= 0, got {window}"
            )
        shorter = window
        longer  = 0
    elif isinstance(window, tuple):
        if len(window) != 2:
            raise ValueError(
                f"window tuple must have exactly 2 elements, got {len(window)}"
            )
        shorter, longer = window
        if shorter < 0 or longer < 0:
            raise ValueError(
                f"window tuple elements must be >= 0, got ({shorter}, {longer})"
            )
    else:
        raise TypeError(
            f"window must be int, (int, int), or None; got {type(window).__name__}"
        )

    win_min = max(1, size - shorter)
    win_max = size + longer
    if win_min > win_max:
        win_min = win_max
    return win_min, win_max


# ---------------------------------------------------------------------------
# Internal token representation
# ---------------------------------------------------------------------------

class _Token:
    """Atomic unit produced by :func:`_tokenize`.

    Each token is either an HTML tag (``is_tag=True``) or a single visible
    character / HTML character reference (``is_tag=False``).
    """

    __slots__ = ("is_tag", "text")

    def __init__(self, is_tag: bool, text: str) -> None:
        self.is_tag: bool = is_tag
        self.text:   str  = text


# ---------------------------------------------------------------------------
# Tokeniser
# ---------------------------------------------------------------------------

def _tokenize(html: str) -> list[_Token]:
    """Split *html* into a flat list of :class:`_Token` objects.

    The function scans left-to-right, greedily consuming — in priority order:

    1. An HTML tag (``_TAG_RE``).
    2. An HTML character reference (``_ENTITY_RE``), treated as one visible
       character.
    3. A single Unicode code point.

    :param html: Raw Telegram HTML string.
    :returns: Ordered list of tokens.
    """
    tokens: list[_Token] = []
    pos = 0
    n   = len(html)

    while pos < n:
        m = _TAG_RE.match(html, pos)
        if m:
            tokens.append(_Token(True, m.group(0)))
            pos = m.end()
            continue

        m = _ENTITY_RE.match(html, pos)
        if m:
            tokens.append(_Token(False, m.group(0)))
            pos = m.end()
            continue

        tokens.append(_Token(False, html[pos]))
        pos += 1

    return tokens


def _visible_len(tokens: list[_Token]) -> int:
    """Return the number of visible-character tokens in *tokens*.

    :param tokens: Token list as produced by :func:`_tokenize`.
    :returns: Count of non-tag tokens.
    """
    return sum(1 for t in tokens if not t.is_tag)


# ---------------------------------------------------------------------------
# Core slicing logic
# ---------------------------------------------------------------------------

def _tag_name(token: _Token) -> str:
    """Extract the lower-cased tag name from a tag token."""
    m = _TAG_RE.match(token.text)
    return m.group("name").lower() if m else ""


def _is_closing(token: _Token) -> bool:
    """Return ``True`` if *token* represents a closing tag (``</...>``)."""
    m = _TAG_RE.match(token.text)
    return bool(m and m.group("close"))


def _pop_by_name(stack: list, name: str) -> None:
    """Remove the last element from *stack* whose tag name equals *name*."""
    for i in range(len(stack) - 1, -1, -1):
        item = stack[i]
        item_name = item if isinstance(item, str) else _tag_name(item)
        if item_name == name:
            stack.pop(i)
            return


def _slice_tokens(tokens: list[_Token], start: int, stop: int) -> list[_Token]:
    """Return tokens corresponding to visible characters ``[start, stop)``.

    The returned token list is *self-contained*: every tag opened before
    *start* and still active at *start* is prepended as an opening tag;
    every tag that remains open at *stop* receives a matching closing tag
    at the end.

    :param tokens: Full token list as produced by :func:`_tokenize`.
    :param start: First visible-character index to include (inclusive).
    :param stop: First visible-character index to exclude (exclusive).
    :returns: Minimal, well-formed token list for the requested range.
    """
    if start >= stop:
        return []

    outer_stack: list[_Token] = []
    suffix_outer: list[_Token] | None = None
    inner_stack: list[str] = []
    body:       list[_Token] = []
    char_count = 0

    for token in tokens:
        if not token.is_tag:
            if char_count < start:
                char_count += 1
            elif char_count < stop:
                if suffix_outer is None:
                    suffix_outer = list(outer_stack)
                body.append(token)
                char_count += 1
            else:
                break
        else:
            closing = _is_closing(token)
            name    = _tag_name(token)

            if char_count < start:
                if not closing:
                    outer_stack.append(token)
                else:
                    _pop_by_name(outer_stack, name)

            elif char_count < stop:
                if suffix_outer is None:
                    suffix_outer = list(outer_stack)
                body.append(token)
                if not closing:
                    inner_stack.append(name)
                else:
                    if any(
                        (s if isinstance(s, str) else _tag_name(s)) == name
                        for s in inner_stack
                    ):
                        _pop_by_name(inner_stack, name)
                    else:
                        _pop_by_name(suffix_outer, name)

    if suffix_outer is None:
        suffix_outer = list(outer_stack)

    prefix = list(outer_stack)
    suffix: list[_Token] = [
        _Token(True, f"</{name}>") for name in reversed(inner_stack)
    ]
    suffix += [
        _Token(True, f"</{_tag_name(t)}>") for t in reversed(suffix_outer)
    ]

    return prefix + body + suffix


def _tokens_to_html(tokens: list[_Token]) -> str:
    """Concatenate token texts into a single HTML string."""
    return "".join(t.text for t in tokens)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class HTMLText:
    """A Telegram HTML-marked-up string with visible-character indexing.

    :class:`HTMLText` wraps a raw Telegram HTML string and exposes a
    sequence interface where all index and slice operations target *visible
    characters* only.  HTML tags are never counted and are automatically
    reopened / closed around any sub-sequence so that the result is always
    a well-formed, standalone Telegram HTML string.

    :param html: Raw Telegram HTML string.
    :type html: str

    **Indexing and slicing**

    Both ``__getitem__`` and slice notation accept negative indices with the
    same semantics as built-in Python sequences::

        >>> msg = HTMLText("My <b>name is <i>Romashka</i></b>")
        >>> len(msg)        # visible chars only
        19
        >>> str(msg[3:-2])
        '<b>name is <i>Romash</i></b>'

    **Streaming**

    :meth:`stream` yields progressively longer :class:`HTMLText` objects,
    useful for typing-effect animations::

        >>> for chunk in HTMLText("<b>Hi</b>").stream():
        ...     print(chunk)
        <b>H</b>
        <b>Hi</b>

    **Supported markup**

    ``<b>``, ``<strong>``, ``<i>``, ``<em>``, ``<u>``, ``<ins>``,
    ``<s>``, ``<strike>``, ``<del>``, ``<code>``,
    ``<pre language="...">``, ``<tg-spoiler>``, ``<blockquote>``,
    ``<a href="...">``, ``<tg-emoji id="...">``,
    and HTML character references (``&amp;``, ``&lt;``, etc.).

    .. note::
        Slice steps other than ``1`` are not supported and raise
        :exc:`ValueError`.
    """

    __slots__ = ("_html", "_tokens", "_length")

    def __init__(self, html: str) -> None:
        self._html:   str          = html
        self._tokens: list[_Token] = _tokenize(html)
        self._length: int          = _visible_len(self._tokens)

    # ------------------------------------------------------------------
    # Sequence protocol
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """Return the number of visible characters (tags excluded)."""
        return self._length

    def __getitem__(self, key: Union[int, slice]) -> "HTMLText":
        """Return a sub-message identified by a visible-character index or slice.

        :param key: An integer index or a :class:`slice` with step ``1``.
        :raises IndexError: If an integer *key* is out of range.
        :raises ValueError: If *key* is a slice with ``step != 1``.
        :raises TypeError: If *key* is neither ``int`` nor ``slice``.
        """
        total = self._length

        if isinstance(key, int):
            idx = key if key >= 0 else total + key
            if idx < 0 or idx >= total:
                raise IndexError("HTMLText index out of range")
            sliced = _slice_tokens(self._tokens, idx, idx + 1)
            return HTMLText(_tokens_to_html(sliced))

        if isinstance(key, slice):
            start, stop, step = key.indices(total)
            if step != 1:
                raise ValueError(
                    "HTMLText slices do not support step != 1; "
                    f"got step={step}"
                )
            sliced = _slice_tokens(self._tokens, start, stop)
            return HTMLText(_tokens_to_html(sliced))

        raise TypeError(
            f"indices must be integers or slices, not {type(key).__name__}"
        )

    def __iter__(self) -> Iterator["HTMLText"]:
        """Iterate over visible characters, each wrapped in its markup context."""
        for i in range(self._length):
            yield self[i]

    def __contains__(self, item: Union[str, "HTMLText"]) -> bool:
        """Return ``True`` if *item* appears in the visible plain text."""
        needle = item.plain if isinstance(item, HTMLText) else item
        return needle in self.plain

    def __bool__(self) -> bool:
        """Return ``True`` if the message contains at least one visible character."""
        return self._length > 0

    # ------------------------------------------------------------------
    # String protocol
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """Return the raw HTML string."""
        return self._html

    def __repr__(self) -> str:
        return f"HTMLText({self._html!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, HTMLText):
            return self._html == other._html
        if isinstance(other, str):
            return self._html == other
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._html)

    def __add__(self, other: Union["HTMLText", str]) -> "HTMLText":
        rhs = other._html if isinstance(other, HTMLText) else other
        return HTMLText(self._html + rhs)

    def __radd__(self, other: Union["HTMLText", str]) -> "HTMLText":
        if isinstance(other, str):
            return HTMLText(other + self._html)
        return NotImplemented

    def __mul__(self, n: int) -> "HTMLText":
        return HTMLText(self._html * n)

    def __rmul__(self, n: int) -> "HTMLText":
        return self.__mul__(n)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def html(self) -> str:
        """The raw Telegram HTML string."""
        return self._html

    @property
    def plain(self) -> str:
        """Visible text with all HTML tags stripped.

        HTML character references are returned in their original encoded form
        (e.g. ``&amp;``, not ``&``).
        """
        return "".join(t.text for t in self._tokens if not t.is_tag)

    # ------------------------------------------------------------------
    # Streaming
    # ------------------------------------------------------------------

    def stream(self, step: int = 1) -> Generator["HTMLText", None, None]:
        """Yield progressively longer HTMLText objects.

        Args:
            step: Number of visible characters added between updates.

        Example:
            >>> for chunk in HTMLText("<b>Hello</b>").stream(step=2):
            ...     print(chunk)
            <b>He</b>
            <b>Hell</b>
            <b>Hello</b>
        """
        if step <= 0:
            raise ValueError("step must be greater than 0")

        for i in range(step, self._length + 1, step):
            yield self[:i]

        if self._length % step:
            yield self[:self._length]

    # ------------------------------------------------------------------
    # Splitting and chunking
    # ------------------------------------------------------------------

    def split_at(self, index: int) -> tuple["HTMLText", "HTMLText"]:
        """Split the message into two parts at a visible-character *index*.

        :param index: Visible-character position at which to split (>= 0).
        :returns: ``(left, right)`` — left covers ``[0, index)``,
                  right covers ``[index, len(self))``.

        Example::

            >>> left, right = HTMLText("<b>Hello</b>").split_at(2)
            >>> str(left), str(right)
            ('<b>He</b>', '<b>llo</b>')
        """
        return self[:index], self[index:]

    def chunk(
        self,
        size: int,
        *,
        split_at: str | tuple[str, ...] | None = None,
        window: Window = None,
    ) -> Generator["HTMLText", None, None]:
        """Yield non-overlapping sub-messages of at most *size* visible characters.

        **Hard cut** (default)::

            chunk(size)
            # Each piece is exactly *size* chars (last may be shorter).

        **Smart splitting** — ``split_at``

        Pass one or more delimiter strings.  The chunk boundary is placed
        *after* the best-matching delimiter occurrence within the allowed
        size window.  If no delimiter falls in the window the chunk falls
        back to a hard cut at *size*.

        ``split_at`` examples:

        * ``" "``         — break only at spaces
        * ``". "``        — break only after ``". "``
        * ``(".", " ")``  — break after a period **or** at a space

        **Size window** — ``window``

        Controls how many characters the actual cut position may deviate
        from *size*.  Accepted forms:

        .. code-block:: text

            window = N          # int  >= 0
                                # chunk may be up to N chars SHORTER than size
                                # search range: [size-N, size]
                                # N=0 → always hard-cut at exactly size

            window = (a, b)     # tuple of two non-negative ints
                                # chunk may be up to a chars SHORTER
                                #           and up to b chars LONGER
                                # search range: [size-a, size+b]

            window = None       # greedy (default): rightmost delimiter
                                # anywhere in [1, size]; no minimum enforced

        Examples:

        .. code-block:: text

            window=10           → [size-10, size]      (up to 10 shorter)
            window=(5, 10)      → [size-5,  size+10]   (5 shorter … 10 longer)
            window=(0, 30)      → [size,    size+30]   (up to 30 longer)
            window=0            → [size,    size]      (exact hard cut)

        Within the window the candidate **closest to** *size* is chosen;
        shorter wins ties.

        :param size: Target number of visible characters per chunk (>= 1).
        :type size: int
        :param split_at: Allowed delimiter string(s), or ``None`` for hard cuts.
        :type split_at: str | tuple[str, ...] | None
        :param window: Size-window specification (see above), or ``None`` for
                       greedy mode.
        :type window: int | tuple[int, int] | None
        :returns: Generator of :class:`HTMLText` chunks.
        :rtype: Generator[HTMLText, None, None]
        :raises ValueError: If *size* < 1 or *window* values are invalid.
        :raises TypeError: If *window* has an unsupported type.

        Examples::

            >>> [str(p) for p in HTMLText("<b>Hello</b>").chunk(2)]
            ['<b>He</b>', '<b>ll</b>', '<b>o</b>']

            >>> art = HTMLText("Hello world. Foo bar baz.")
            >>> [str(p) for p in art.chunk(14, split_at=". ")]
            ['Hello world. ', 'Foo bar baz.']

            >>> art = HTMLText("Hello world foo bar")
            >>> [str(p) for p in art.chunk(10, split_at=" ", window=(0, 5))]
            ['Hello ', 'world foo ', 'bar']
        """
        if size < 1:
            raise ValueError(f"chunk size must be >= 1, got {size}")

        # ── fast path: no smart options ──────────────────────────────────
        if split_at is None and window is None:
            for i in range(0, self._length, size):
                yield self[i : i + size]
            return

        # ── resolve window ────────────────────────────────────────────────
        win_min, win_max = _resolve_window(window, size)
        _greedy = (window is None)

        # Special case: window=0 → always hard cut, ignore delimiters.
        _hard_cut_only = (
            isinstance(window, int) and window == 0
        ) or (
            isinstance(window, tuple) and window == (0, 0)
        )

        # ── normalise split_at ────────────────────────────────────────────
        needles: tuple[str, ...] = (
            ()           if split_at is None           else
            (split_at,)  if isinstance(split_at, str)  else
            tuple(split_at)
        )

        plain = self.plain
        pos   = 0
        total = self._length

        while pos < total:
            remaining = total - pos

            # Remainder fits inside the max window — emit it whole.
            if remaining <= win_max:
                yield self[pos:]
                break

            # ── hard-cut path ─────────────────────────────────────────────
            if _hard_cut_only or not needles:
                cut = min(size, remaining)
                yield self[pos : pos + cut]
                pos += cut
                continue

            # ── locate split candidates ───────────────────────────────────
            segment    = plain[pos : pos + win_max]
            candidates: list[int] = []

            for needle in needles:
                nlen = len(needle)
                idx  = segment.find(needle)
                while idx != -1:
                    end_pos = idx + nlen
                    if win_min <= end_pos <= win_max:
                        candidates.append(end_pos)
                    idx = segment.find(needle, idx + 1)

            if not candidates:
                cut = min(size, remaining)   # no delimiter in window - hard cut

            elif _greedy:
                cut = max(candidates)        # rightmost position ≤ size

            else:
                unique = sorted(set(candidates))
                cut    = min(unique, key=lambda x: (abs(x - size), x))

            yield self[pos : pos + cut]
            pos += cut

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def find(self, sub: str) -> int:
        """Return the lowest visible-text index where *sub* starts, or ``-1``."""
        return self.plain.find(sub)

    def startswith(self, prefix: str) -> bool:
        """Return ``True`` if the visible text starts with *prefix*."""
        return self.plain.startswith(prefix)

    def endswith(self, suffix: str) -> bool:
        """Return ``True`` if the visible text ends with *suffix*."""
        return self.plain.endswith(suffix)

    # ------------------------------------------------------------------
    # Case transformations
    # ------------------------------------------------------------------

    def upper(self) -> "HTMLText":
        """Return a copy with visible text converted to upper case.

        Example::

            >>> str(HTMLText("<b>hello</b>").upper())
            '<b>HELLO</b>'
        """
        return HTMLText("".join(
            t.text.upper() if not t.is_tag else t.text
            for t in self._tokens
        ))

    def lower(self) -> "HTMLText":
        """Return a copy with visible text converted to lower case.

        Example::

            >>> str(HTMLText("<b>HELLO</b>").lower())
            '<b>hello</b>'
        """
        return HTMLText("".join(
            t.text.lower() if not t.is_tag else t.text
            for t in self._tokens
        ))

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def is_empty(self) -> bool:
        """Return ``True`` if there are no visible characters."""
        return self._length == 0

    def count_chars(self) -> int:
        """Return the visible-character count (alias for ``len(self)``)."""
        return self._length

    # ------------------------------------------------------------------
    # Class-level helpers
    # ------------------------------------------------------------------

    @classmethod
    def join(
        cls,
        separator: Union[str, "HTMLText"],
        parts: list[Union[str, "HTMLText"]],
    ) -> "HTMLText":
        """Concatenate *parts* with *separator* between each element.

        Example::

            >>> str(HTMLText.join(", ", [HTMLText("<b>A</b>"), HTMLText("<i>B</i>")]))
            '<b>A</b>, <i>B</i>'
        """
        sep   = separator._html if isinstance(separator, HTMLText) else separator
        items = [p._html if isinstance(p, HTMLText) else p for p in parts]
        return cls(sep.join(items))

    @classmethod
    def from_plain(cls, text: str) -> "HTMLText":
        """Create an :class:`HTMLText` from a plain string, escaping HTML specials.

        The characters ``&``, ``<``, and ``>`` are replaced with their
        corresponding character references.

        Example::

            >>> str(HTMLText.from_plain("<b>test</b>"))
            '&lt;b&gt;test&lt;/b&gt;'
        """
        escaped = (
            text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        return cls(escaped)


if __name__ == "__main__":
    import time
    msg = HTMLText("My <b>name is <i>Romashka</i></b>")

    print(len(msg))               # 19
    print(msg[3:-2])              # <b>name is <i>Romash</i></b>
    print(msg[12])                # <b><i>o</i></b>
    print(msg.plain)              # My name is Romashka

    left, right = msg.split_at(7)
    print(left)                   # My <b>na</b>
    print(right)                  # <b>me is <i>Romashka</i></b>

    for part in msg.chunk(4):
        print(part)

    # window examples
    art = HTMLText("Hello world foo bar baz qux")
    print("\nwindow=5 (up to 5 shorter):")
    for p in art.chunk(10, split_at=" ", window=5):
        print(f"  {repr(str(p))} ({len(p)})")

    print("\nwindow=(3, 5) (3 shorter…5 longer):")
    for p in art.chunk(10, split_at=" ", window=(3, 5)):
        print(f"  {repr(str(p))} ({len(p)})")

    print("\nwindow=(0, 10) (up to 10 longer):")
    for p in art.chunk(10, split_at=" ", window=(0, 10)):
        print(f"  {repr(str(p))} ({len(p)})")

    for chunk in msg.stream():
        print(chunk, end="\r")
        time.sleep(0.3)

    print()
