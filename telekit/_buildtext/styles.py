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
from typing import Union, Literal, TYPE_CHECKING, Union, Any
from urllib.parse import quote
import html as _html

if TYPE_CHECKING: # Union[str, "TextEntity", "Template"]
    from string.templatelib import Template # pyright: ignore[reportMissingImports]

import telebot.formatting

import telekit.utils

from .formatter import TextEntity, EasyTextEntity, StaticTextEntity, EasyTextEntityWithPostRender, Group


class Bold(EasyTextEntity):
    """
    Applies **bold formatting** to the provided content.

    :param content: One or more strings or ``TextEntity`` objects to format.
    :param escape: Whether to escape HTML/Markdown special characters in plain string content.
        Defaults to ``True``.

        Example::

            Bold("<i>Hello").html                 # "<b>&lt;i&gt;Hello</b>"
            Bold("<i>Hello", escape=False).html   # "<b><i>Hello</b>"

    :param sep: Separator inserted between multiple content elements.
        Defaults to ``""``.
    :param enabled: If falsy, renders content without bold formatting.
        Defaults to ``True``.

    Examples::

        Bold("Hello").html      # "<b>Hello</b>"
        Bold("Hello").markdown  # "*Hello*"

        Bold("Hello", "World", sep=" ").html  # "<b>Hello World</b>"

        Bold("title", enabled=is_important).html  # "title" if not is_important

        sender.set_text(Bold("Hello!"))

    `Documentation <https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md>`_ · on GitHub
    """

    def _render_markdown(self, content: str) -> str:
        return telebot.formatting.mbold(content, escape=False)

    def _render_html(self, content: str) -> str:
        return f"<b>{content}</b>"


class Italic(EasyTextEntity):
    """
    Applies *italic formatting* to the provided content.

    :param content: One or more strings or ``TextEntity`` objects to format.
    :param escape: Whether to escape HTML/Markdown special characters in plain string content.
        Defaults to ``True``.

        Example::

            Italic("<b>Hello").html                 # "<i>&lt;b&gt;Hello</i>"
            Italic("<b>Hello", escape=False).html   # "<i><b>Hello</i>"

    :param sep: Separator inserted between multiple content elements.
        Defaults to ``""``.
    :param enabled: If falsy, renders content without italic formatting.
        Defaults to ``True``.

    Examples::

        Italic("Hello").html      # "<i>Hello</i>"
        Italic("Hello").markdown  # "_Hello_"

        sender.set_text(Italic("note"))

    `Documentation <https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md>`_ · on GitHub
    """

    def _render_markdown(self, content: str) -> str:
        return telebot.formatting.mitalic(content, escape=False)

    def _render_html(self, content: str) -> str:
        return f"<i>{content}</i>"


class Underline(EasyTextEntity):
    """
    Applies <u>underline formatting</u> to the provided content.

    :param content: One or more strings or ``TextEntity`` objects to format.
    :param escape: Whether to escape HTML/Markdown special characters in plain string content.
        Defaults to ``True``.

        Example::

            Underline("<b>Hello").html                 # "<u>&lt;b&gt;Hello</u>"
            Underline("<b>Hello", escape=False).html   # "<u><b>Hello</u>"

    :param sep: Separator inserted between multiple content elements.
        Defaults to ``""``.
    :param enabled: If falsy, renders content without underline formatting.
        Defaults to ``True``.

    Examples::

        Underline("Hello").html      # "<u>Hello</u>"
        Underline("Hello").markdown  # "__Hello__"

        sender.set_text(Underline("important"))

    `Documentation <https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md>`_ · on GitHub
    """

    def _render_markdown(self, content: str) -> str:
        return telebot.formatting.munderline(content, escape=False)

    def _render_html(self, content: str) -> str:
        return f"<u>{content}</u>"


class Strikethrough(EasyTextEntity):
    """
    Applies <s>strikethrough</s> formatting to the provided content.

    :param content: One or more strings or ``TextEntity`` objects to format.
    :param escape: Whether to escape HTML/Markdown special characters in plain string content.
        Defaults to ``True``.

        Example::

            Strikethrough("<b>Hello").html                 # "<s>&lt;b&gt;Hello</s>"
            Strikethrough("<b>Hello", escape=False).html   # "<s><b>Hello</s>"

    :param sep: Separator inserted between multiple content elements.
        Defaults to ``""``.
    :param enabled: If falsy, renders content without strikethrough formatting.
        Defaults to ``True``.

    Examples::

        Strikethrough("Hello").html      # "<s>Hello</s>"
        Strikethrough("Hello").markdown  # "~~Hello~~"

        sender.set_text(Strikethrough("old price"))

    `Documentation <https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md>`_ · on GitHub
    """

    def _render_markdown(self, content: str) -> str:
        return telebot.formatting.mstrikethrough(content, escape=False)

    def _render_html(self, content: str) -> str:
        return f"<s>{content}</s>"


class Code(EasyTextEntity):
    """
    Formats the content as inline <code>monospace</code> code.

    The rendered text can also be copied by simply tapping on it in Telegram.

    :param content: One or more strings or ``TextEntity`` objects to format.
    :param escape: Whether to escape HTML/Markdown special characters in plain string content.
        Defaults to ``True``.

        Example::

            Code("<b>tag").html                 # "<code>&lt;b&gt;tag</code>"
            Code("<b>tag", escape=False).html   # "<code><b>tag</code>"

    :param sep: Separator inserted between multiple content elements.
        Defaults to ``""``.
    :param enabled: If falsy, renders content without code formatting.
        Defaults to ``True``.

    Examples::

        Code("print('hello')").html      # "<code>print('hello')</code>"
        Code("print('hello')").markdown  # "`print('hello')`"

        sender.set_text(Code("/start"))

    `Documentation <https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md>`_ · on GitHub
    """

    def _render_markdown(self, content: str) -> str:
        return f"`{content}`"

    def _render_html(self, content: str) -> str:
        return f"<code>{content}</code>"


class Language(EasyTextEntity):
    """
    Formats the content as a code block with syntax highlighting for the specified language.

    :param content: One or more strings or ``TextEntity`` objects to format.
    :param lang: The programming language identifier used for syntax highlighting
        (e.g. ``"python"``, ``"javascript"``, ``"bash"``).
    :param escape: Whether to escape HTML/Markdown special characters in plain string content.
        Defaults to ``True``.

        Example::

            Language("x = 1", lang="python", escape=False).html
            # '<pre language="python">x = 1\\n</pre>\\n'

    :param sep: Separator inserted between multiple content elements.
        Defaults to ``""``.
    :param enabled: If falsy, renders content without code block formatting.
        Defaults to ``True``.

    Examples::

        Language("x = 1", lang="python").markdown
        # "```python\\nx = 1```"

        Language("console.log(1)", lang="javascript").html
        # '<pre language="javascript">console.log(1)\\n</pre>\\n'

        sender.set_text(Language("x = 1", lang="python"))

    `Documentation <https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md>`_ · on GitHub
    """

    def __init__(self, *content, lang: str, escape: bool = True, sep: Union[str, "TextEntity", "Template"] = "", enabled: bool | Any = True):
        self._language: str = lang
        super().__init__(*content, escape=escape, sep=sep, enabled=enabled)

    def _render_markdown(self, content: str) -> str:
        return telebot.formatting.mcode(content, language=self._language, escape=False)

    def _render_html(self, content: str) -> str:
        return f'<pre language="{self._language}">{content}\n</pre>\n'


class Python(Language):
    """
    Formats the content as a Python code block with syntax highlighting.

    A shorthand for ``Language(..., lang="python")``.

    :param content: One or more strings or ``TextEntity`` objects to format.
    :param escape: Whether to escape HTML/Markdown special characters in plain string content.
        Defaults to ``True``.

        Example::

            Python("x = 1", escape=False).html
            # '<pre language="python">x = 1\\n</pre>\\n'

    :param sep: Separator inserted between multiple content elements.
        Defaults to ``""``.
    :param enabled: If falsy, renders content without code block formatting.
        Defaults to ``True``.

    Examples::

        Python("x = 1").markdown  # "```python\\nx = 1```"
        Python("x = 1").html      # '<pre language="python">x = 1\\n</pre>\\n'

        sender.set_text(Python("def hello(): pass"))

    `Documentation <https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md>`_ · on GitHub
    """

    def __init__(self, *content, escape: bool = True, sep: Union[str, "TextEntity", "Template"] = "", enabled: bool | Any = True):
        super().__init__(*content, lang="python", escape=escape, sep=sep, enabled=enabled)


class Spoiler(EasyTextEntity):
    """
    Hides the content behind a spoiler that can be revealed by the user.

    :param content: One or more strings or ``TextEntity`` objects to format.
    :param escape: Whether to escape HTML/Markdown special characters in plain string content.
        Defaults to ``True``.

        Example::

            Spoiler("<b>Hello").html                 # "<tg-spoiler>&lt;b&gt;Hello</tg-spoiler>"
            Spoiler("<b>Hello", escape=False).html   # "<tg-spoiler><b>Hello</tg-spoiler>"

    :param sep: Separator inserted between multiple content elements.
        Defaults to ``""``.
    :param enabled: If falsy, renders content without spoiler formatting.
        Defaults to ``True``.

    Examples::

        Spoiler("secret").html      # "<tg-spoiler>secret</tg-spoiler>"
        Spoiler("secret").markdown  # "||secret||"

        sender.set_text(Spoiler("plot twist"))

    `Documentation <https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md>`_ · on GitHub
    """

    def _render_markdown(self, content: str) -> str:
        return telebot.formatting.mspoiler(content, escape=False)

    def _render_html(self, content: str) -> str:
        return f'<tg-spoiler>{content}</tg-spoiler>'


class Quote(EasyTextEntityWithPostRender):
    """
    Formats the content as a quoted message block.

    :param content: One or more strings or ``TextEntity`` objects to format.
    :param expandable: Whether the quote can be collapsed and expanded by the user.
        Defaults to ``False``.
    :param end: String appended after the rendered quote. Defaults to ``"\\n"``.
    :param escape: Whether to escape HTML/Markdown special characters in plain string content.
        Defaults to ``True``.

        Example::

            Quote("<b>Hello").html                 # "<blockquote>&lt;b&gt;Hello</blockquote>\\n"
            Quote("<b>Hello", escape=False).html   # "<blockquote><b>Hello</blockquote>\\n"

    :param sep: Separator inserted between multiple content elements.
        Defaults to ``""``.
    :param enabled: If falsy, renders content without quote formatting.
        Defaults to ``True``.

    Examples::

        Quote("Be yourself.").html
        # "<blockquote>Be yourself.</blockquote>\\n"

        Quote("Very long text...", expandable=True).html
        # expandable blockquote

        sender.set_text(Quote("Note: this is important"))

    `Documentation <https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md>`_ · on GitHub
    """

    def __init__(self, *content, expandable: bool = False, end: str = "\n", escape: bool = True, sep: Union[str, "TextEntity", "Template"] = "", enabled: bool | Any = True):
        self._expandable: bool = expandable
        self._end: str = end
        super().__init__(*content, escape=escape, sep=sep, enabled=enabled)

    def _render_markdown(self, content: str) -> str:
        return telebot.formatting.mcite(content, escape=False, expandable=self._expandable)

    def _render_html(self, content: str) -> str:
        return telebot.formatting.hcite(content, escape=False, expandable=self._expandable)

    def _post_render(self, rendered: str) -> str:
        return rendered + self._end if self._end else rendered


class Escape(TextEntity):
    """
    Escapes special characters according to `parse_mode`, making the text safe for rendering.

    By default, all plain strings passed to style classes are already escaped.
    Use this explicitly when you need to ensure a string is always escaped
    regardless of context.

    :param content: One or more strings or ``TextEntity`` objects to escape.
    :param sep: Separator inserted between multiple content elements.
        Defaults to ``""``.

    Examples::

        Escape("<b>Hello</b>").html      # "&lt;b&gt;Hello&lt;/b&gt;"
        Escape("<b>Hello</b>").markdown  # "\\<b\\>Hello\\<\\/b\\>"

        sender.set_text(Escape(user_input))

    `Documentation <https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md>`_ · on GitHub
    """

    def __init__(self, *content, sep: Union[str, "TextEntity", "Template"] = ""):
        super().__init__(*content, escape=True, sep=sep)


class Raw(TextEntity):
    """
    Passes content without escaping special characters, even when `parse_mode` is active.

    Allows interpreting all HTML tags or Markdown syntax directly — depending on
    the ``parse_mode`` of the ``Sender``. By default, all tags not created via
    style classes are escaped automatically; this class disables that behavior.

    :param content: One or more strings or ``TextEntity`` objects to pass through unescaped.
    :param sep: Separator inserted between multiple content elements.
        Defaults to ``""``.

    Examples::

        Raw("<b>Hello</b>").html  # "<b>Hello</b>"  → rendered as bold in Telegram

        sender.set_text(Raw("<b>important</b>") + " message")

    `Documentation <https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md>`_ · on GitHub
    """

    def __init__(self, *content, sep: Union[str, "TextEntity", "Template"] = ""):
        super().__init__(*content, escape=False, sep=sep)


class Link(EasyTextEntity):
    """
    Creates a clickable hyperlink from the content pointing to the specified URL.

    :param content: One or more strings or ``TextEntity`` objects used as the link label.
    :param url: The target URL the link points to.
    :param escape: Whether to escape HTML/Markdown special characters in plain string content.
        Defaults to ``True``.

        Example::

            >>> Link("<b>Click", url="https://example.com").html
            '<a href="https://example.com">&lt;b&gt;Click</a>'

            >>> Link("<b>Click", url="https://example.com", escape=False).html
            '<a href="https://example.com"><b>Click</a>'

    :param sep: Separator inserted between multiple content elements.
        Defaults to ``""``.
    :param enabled: If falsy, renders content without link formatting.
        Defaults to ``True``.

    Examples::

        >>> Link("Open site", url="https://example.com").html
        '<a href="https://example.com">Open site</a>'

        >>> Link("Open site", url="https://example.com").markdown
        "[Open site](https://example.com)"

        >>> Link("Open site", url="https://example.com").none
        "Open site (https://example.com)"

        sender.set_text(Link(Bold("Telekit on GitHub"), url="https://github.com/Romashkaa/telekit"))

    `Documentation <https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md>`_ · on GitHub
    """

    def __init__(self, *content, url: str, escape: bool = True, sep: Union[str, "TextEntity", "Template"] = "", enabled: bool | Any = True):
        self._url: str = url
        super().__init__(*content, escape=escape, sep=sep, enabled=enabled)

    def _render_markdown(self, content: str) -> str:
        return f"[{content}]({self._url})"

    def _render_html(self, content: str) -> str:
        return f'<a href="{self._url}">{content}</a>'

    def _render_none(self, content: str) -> str:
        return f"{content} ({self._url})"


class Mention(Link):
    """
    Creates a Telegram mention link by user ID.

    Unlike ``UserLink``, this class uses the user's unique numeric ID
    instead of a username, which means it works even if the user has
    no public username set.

    :param content: One or more strings or ``TextEntity`` objects used as the link label.
    :param user_id: The unique Telegram user ID of the target user.
    :param escape: Whether to escape HTML/Markdown special characters in plain string content.
        Defaults to ``True``.
    :param sep: Separator inserted between multiple content elements.
        Defaults to ``""``.
    :param enabled: If falsy, renders content without mention link formatting.
        Defaults to ``True``.

    Examples::

        Mention("John", user_id=123456789).html
        # '<a href="tg://user?id=123456789">John</a>'

        Mention("John", user_id=123456789).markdown
        # "[John](tg://user?id=123456789)"

        sender.set_text(Mention(user.first_name, user_id=user.id))

    `Documentation <https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md>`_ · on GitHub
    """

    def __init__(self, *content, user_id: int | str, escape: bool = True, sep: Union[str, "TextEntity", "Template"] = "", enabled: bool | Any = True):
        url: str = telekit.utils.make_mention(user_id)
        super().__init__(*content, url=url, escape=escape, sep=sep, enabled=enabled)


class UserLink(Link):
    """
    Creates a Telegram user link by username.

    When the user taps the link, it opens a chat with the specified user.
    If ``text`` is provided, it will be pre-filled in the message input field
    as a suggestion when the link is opened.

    :param content: One or more strings or ``TextEntity`` objects used as the link label.
    :param username: Telegram username of the target user (with or without ``@``).
    :param text: Optional text to pre-fill in the message input field when the link is opened.
        Defaults to ``None``.
    :param escape: Whether to escape HTML/Markdown special characters in plain string content.
        Defaults to ``True``.
    :param sep: Separator inserted between multiple content elements.
        Defaults to ``""``.
    :param enabled: If falsy, renders content without user link formatting.
        Defaults to ``True``.

    Examples::

        UserLink("Contact support", username="support_manager").html
        # '<a href="https://t.me/support_manager">Contact support</a>'

        UserLink("Say hi", username="john2004", text="Hello!").html
        # '<a href="https://t.me/john2004?text=Hello%21">Say hi</a>'

    `Documentation <https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md>`_ · on GitHub
    """

    def __init__(self, *content, username: str, text: str | None = None, escape: bool = True, sep: Union[str, "TextEntity", "Template"] = "", enabled: bool | Any = True):
        url: str = telekit.utils.make_user_link(username, text)
        super().__init__(*content, url=url, escape=escape, sep=sep, enabled=enabled)


class BotLink(Link):
    """
    Creates a Telegram bot deep link with an optional start parameter.

    Allows passing data to the bot when the user opens it via the link,
    which is useful for referral systems, onboarding flows, and deep linking.

    :param content: One or more strings or ``TextEntity`` objects used as the link label.
    :param username: Telegram username of the target bot (with or without ``@``).
    :param start: Optional deep link parameter passed to the bot as the ``/start`` argument.
        Defaults to ``None``.
    :param escape: Whether to escape HTML/Markdown special characters in plain string content.
        Defaults to ``True``.
    :param sep: Separator inserted between multiple content elements.
        Defaults to ``""``.
    :param enabled: If falsy, renders content without bot link formatting.
        Defaults to ``True``.

    Examples::

        BotLink("Open bot", username="my_bot").html
        # '<a href="https://t.me/my_bot">Open bot</a>'

        BotLink("Get started", username="my_bot", start="ref_123").html
        # '<a href="https://t.me/my_bot?start=ref_123">Get started</a>'

    `Documentation <https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md>`_ · on GitHub
    """

    def __init__(self, *content, username: str, start: str | None = None, escape: bool = True, sep: Union[str, "TextEntity", "Template"] = "", enabled: bool | Any = True):
        url: str = telekit.utils.make_bot_link(username, start)
        super().__init__(*content, url=url, escape=escape, sep=sep, enabled=enabled)


class EncodeURL(StaticTextEntity):
    """
    URL-encodes the provided content string.

    Useful for safely embedding dynamic values inside URLs, such as query
    parameters or deep link payloads.

    :param content: One or more strings to URL-encode. ``TextEntity`` objects are not supported.

    Examples::

        EncodeURL("hello world").html  # "hello%20world"
        EncodeURL("a=1&b=2").html      # "a%3D1%26b%3D2"

    `Documentation <https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md>`_ · on GitHub
    """

    def _render_any(self, content: str) -> str:
        return quote(content, safe="")


class Stack(TextEntity):
    """
    Renders a list of items as a formatted stack with a customizable prefix per line.

    By default, items are numbered automatically using ``{{index}}``.
    You can also use any of the predefined ``Stack.Markers`` as the ``start`` prefix
    to create bulleted lists.

    :param content: One or more strings or ``TextEntity`` objects representing list items.
    :param start: Prefix for each item. Use ``{{index}}`` as a placeholder that will be
        replaced with the auto-incrementing line number. Defaults to ``"{{index}}. "``.

        Example::

            >>> Stack("A", "B", start="- {{index}}. ").html
            \"""
            - 1. A
            - 2. B
            \"""

            >>> Stack("A", "B", start=Stack.Markers.DOT).html
            \"""
            • A
            • B
            \"""

    :param sep: Separator appended at the end of each item except the last.
        Defaults to ``"\\n"``.

        Example::

            >>> Stack("A", "B", "C", sep=";\\n").html
            \"""
            1. A;
            2. B;
            3. C
            \"""

    :param end: Appended after the last item, e.g. a closing punctuation mark.
        Defaults to ``""``.

        Example::

            >>> Stack("A", "B", end=".").none
            \"""
            1. A
            2. B.
            \"""

    :param escape: Whether to escape HTML/Markdown special characters in plain string content.
        Defaults to ``True``.
    :param enabled: If falsy, renders content without stack formatting.
        Defaults to ``True``.

    Examples::

        Stack("Buy milk", "Walk the dog", "Read a book").html
        \"""
        1. Buy milk
        2. Walk the dog
        3. Read a book
        \"""

        Stack("Buy milk", "Walk the dog", start=Stack.Markers.CHECK).html
        \"""
        ✓ Buy milk
        ✓ Walk the dog
        \"""

        Stack("Step one", "Step two", sep=";\\n", end=".").html
        \"""
        1. Step one;
        2. Step two.
        \"""

        sender.set_text(Stack("Item 1", "Item 2", "Item 3"))

    `Documentation <https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md>`_ · on GitHub
    """

    class Markers:
        LINE = "- "
        DOT = "• "
        TRIANGLE = "‣ "
        TRIANGLE_BIG = "▸ "
        TRIANGLE_OUTLINE = "› "
        ARROW = "→ "
        ARROW_R = ARROW
        ARROW_L = "← "
        ARROW_D = "↓ "
        ARROW_U = "↑ "
        FINGER = "☞ "
        STAR = "★ "
        STAR_OUTLINE = "☆ "
        CHECK = "✓ "
        CROSS = "✕ "

    def __init__(self, *content, start: str = "{{index}}. ", sep: Union[str, "TextEntity", "Template"] = "\n", end: Union[str, "TextEntity", "Template"] = "", escape: bool = True, enabled: bool | Any = True):
        self._start = start
        self._end = end
        super().__init__(*content, escape=escape, sep=sep, enabled=enabled)

    def _render_content(self, parse_mode: None | Literal['html'] | Literal['markdown']) -> str:
        if not self._enabled:
            # render content without stack formatting
            end: str = self._render_item(self._end, parse_mode)
            content = super()._render_content(parse_mode)
            return f"\n{content}{end}\n"
        
        stack: list[str] = []

        for index, item in enumerate(self._content, start=1):
            stack.append(
                Group(
                    self._start.replace("{{index}}", str(index)),
                    item,
                    escape=self._escape_strings
                ).render(parse_mode)
            )

        sep: str = self._render_item(self._separator, parse_mode)
        end: str = self._render_item(self._end, parse_mode)
        
        content: str = sep.join(stack)

        return f"\n{content}{end}\n"



# ---------------------------------------------------------------------------------
# Rich HTML styles (Bot API 10.1+). Use together with sender.set_rich_html(True)
# ---------------------------------------------------------------------------------

def _attrs(**attrs) -> str:
    """Builds an HTML attribute string. `True` -> bare attribute, None/False -> skipped."""
    parts = []
    for key, value in attrs.items():
        if value is None or value is False:
            continue
        key = key.replace("_", "-")
        if value is True:
            parts.append(key)
        else:
            parts.append(f'{key}="{_html.escape(str(value), quote=True)}"')
    return (" " + " ".join(parts)) if parts else ""


class RichEntity(EasyTextEntity):
    """
    ⚠️ Works only in Rich mode (``sender.set_rich_html(True)``).

    Base class for styles that exist only in Rich HTML.
    Outside of rich mode the sender downgrades these tags to plain formatting
    (or drops them) and prints a warning.
    """


# -- inline

class Marked(RichEntity):
    """⚠️ Works only in Rich mode (``sender.set_rich_html(True)``).

    Highlighted text: ``<mark>``."""
    def _render_html(self, content: str) -> str:
        return f"<mark>{content}</mark>"


class Subscript(RichEntity):
    """⚠️ Works only in Rich mode (``sender.set_rich_html(True)``).

    Subscript: ``<sub>``."""
    def _render_html(self, content: str) -> str:
        return f"<sub>{content}</sub>"


class Superscript(RichEntity):
    """⚠️ Works only in Rich mode (``sender.set_rich_html(True)``).

    Superscript: ``<sup>``."""
    def _render_html(self, content: str) -> str:
        return f"<sup>{content}</sup>"


class CustomEmoji(EasyTextEntity):
    """
    Custom emoji: ``<tg-emoji emoji-id="...">fallback</tg-emoji>``.
    Works both in regular HTML and in Rich HTML. The content is the fallback emoji.

    Example::

        CustomEmoji("👍", emoji_id=5368324170671202286)
    """
    def __init__(self, *content, emoji_id: int | str, escape: bool = True, sep: Union[str, "TextEntity", "Template"] = "", enabled: bool | Any = True):
        self._emoji_id = emoji_id
        super().__init__(*content, escape=escape, sep=sep, enabled=enabled)

    def _render_html(self, content: str) -> str:
        return f"<tg-emoji{_attrs(emoji_id=self._emoji_id)}>{content}</tg-emoji>"


class DateTime(RichEntity):
    """
    ⚠️ Works only in Rich mode (``sender.set_rich_html(True)``).

    Formatted date and time: ``<tg-time unix="..." format="...">``.

    Example::

        DateTime("22:45 tomorrow", unix=1647531900, format="wDT")
    """
    def __init__(self, *content, unix: int, format: str | None = None, escape: bool = True, sep: Union[str, "TextEntity", "Template"] = "", enabled: bool | Any = True):
        self._unix = unix
        self._format = format
        super().__init__(*content, escape=escape, sep=sep, enabled=enabled)

    def _render_html(self, content: str) -> str:
        return f"<tg-time{_attrs(unix=self._unix, format=self._format)}>{content}</tg-time>"


class Math(RichEntity):
    """⚠️ Works only in Rich mode (``sender.set_rich_html(True)``).

    Inline LaTeX formula: ``<tg-math>``. The content is treated as raw LaTeX."""
    def _render_html(self, content: str) -> str:
        return f"<tg-math>{content}</tg-math>"


class MathBlock(RichEntity):
    """⚠️ Works only in Rich mode (``sender.set_rich_html(True)``).

    Block LaTeX formula: ``<tg-math-block>``."""
    def _render_html(self, content: str) -> str:
        return f"<tg-math-block>{content}</tg-math-block>"


class Anchor(RichEntity):
    """⚠️ Works only in Rich mode (``sender.set_rich_html(True)``).

    Anchor definition: ``<a name="..."></a>``. Target for ``AnchorLink``."""
    def __init__(self, name: str, *, enabled: bool | Any = True):
        self._name = name
        super().__init__(enabled=enabled)

    def _render_html(self, content: str) -> str:
        return f"<a{_attrs(name=self._name)}></a>"


class AnchorLink(RichEntity):
    """
    ⚠️ Works only in Rich mode (``sender.set_rich_html(True)``).

    Link to an anchor or to a reference: ``<a href="#name">``.
    An empty ``name`` links back to the top of the message.
    """
    def __init__(self, *content, name: str = "", escape: bool = True, sep: Union[str, "TextEntity", "Template"] = "", enabled: bool | Any = True):
        self._name = name
        super().__init__(*content, escape=escape, sep=sep, enabled=enabled)

    def _render_html(self, content: str) -> str:
        return f"<a{_attrs(href='#' + self._name)}>{content}</a>"


class Reference(RichEntity):
    """⚠️ Works only in Rich mode (``sender.set_rich_html(True)``).

    Footnote definition: ``<tg-reference name="...">``. Link to it with ``AnchorLink``."""
    def __init__(self, *content, name: str, escape: bool = True, sep: Union[str, "TextEntity", "Template"] = "", enabled: bool | Any = True):
        self._name = name
        super().__init__(*content, escape=escape, sep=sep, enabled=enabled)

    def _render_html(self, content: str) -> str:
        return f"<tg-reference{_attrs(name=self._name)}>{content}</tg-reference>"


# -- text blocks

class Heading(RichEntity):
    """⚠️ Works only in Rich mode (``sender.set_rich_html(True)``).

    Heading ``<h1>``..``<h6>``; ``level=1`` is the largest."""
    def __init__(self, *content, level: int = 1, escape: bool = True, sep: Union[str, "TextEntity", "Template"] = "", enabled: bool | Any = True):
        if not 1 <= level <= 6:
            raise ValueError("Heading level must be between 1 and 6")
        self._level = level
        super().__init__(*content, escape=escape, sep=sep, enabled=enabled)

    def _render_html(self, content: str) -> str:
        return f"<h{self._level}>{content}</h{self._level}>"

    def _render_markdown(self, content: str) -> str:
        return telebot.formatting.mbold(content, escape=False) + "\n"


class Paragraph(RichEntity):
    """⚠️ Works only in Rich mode (``sender.set_rich_html(True)``).

    Paragraph: ``<p>``."""
    def _render_html(self, content: str) -> str:
        return f"<p>{content}</p>"


class Footer(RichEntity):
    """⚠️ Works only in Rich mode (``sender.set_rich_html(True)``).

    Footer: ``<footer>``."""
    def _render_html(self, content: str) -> str:
        return f"<footer>{content}</footer>"


class Divider(RichEntity):
    """⚠️ Works only in Rich mode (``sender.set_rich_html(True)``).

    Horizontal divider: ``<hr/>``."""
    def __init__(self, *, enabled: bool | Any = True):
        super().__init__(enabled=enabled)

    def _render_html(self, content: str) -> str:
        return "<hr/>"

    def _render_markdown(self, content: str) -> str:
        return "———\n"

    def _render_none(self, content: str) -> str:
        return "———\n"


class Cite(RichEntity):
    """⚠️ Works only in Rich mode (``sender.set_rich_html(True)``).

    Author/credit line: ``<cite>``. Use inside ``Quote`` or ``PullQuote``."""
    def _render_html(self, content: str) -> str:
        return f"<cite>{content}</cite>"


class PullQuote(RichEntity):
    """⚠️ Works only in Rich mode (``sender.set_rich_html(True)``).

    Centered pull quotation: ``<aside>`` with an optional credit."""
    def __init__(self, *content, credit: Union[str, "TextEntity", "Template", None] = None, escape: bool = True, sep: Union[str, "TextEntity", "Template"] = "", enabled: bool | Any = True):
        self._credit = credit
        super().__init__(*content, escape=escape, sep=sep, enabled=enabled)

    def _render_html(self, content: str) -> str:
        credit = ""
        if self._credit is not None:
            credit = f"<cite>{self._render_item(self._credit, 'html')}</cite>"
        return f"<aside>{content}{credit}</aside>"


class Details(RichEntity):
    """
    ⚠️ Works only in Rich mode (``sender.set_rich_html(True)``).

    Collapsible block: ``<details><summary>``.

    Example::

        Details("Hidden text", summary="Click me", is_open=False)
    """
    def __init__(self, *content, summary: Union[str, "TextEntity", "Template"], is_open: bool = False, escape: bool = True, sep: Union[str, "TextEntity", "Template"] = "", enabled: bool | Any = True):
        self._summary = summary
        self._is_open = is_open
        super().__init__(*content, escape=escape, sep=sep, enabled=enabled)

    def _render_html(self, content: str) -> str:
        summary = self._render_item(self._summary, "html")
        return f"<details{_attrs(open=self._is_open)}><summary>{summary}</summary>{content}</details>"


# -- lists

class ListItem(RichEntity):
    """⚠️ Works only in Rich mode (``sender.set_rich_html(True)``).

    List item ``<li>`` with optional explicit ``value`` and ``type`` (ordered lists)."""
    def __init__(self, *content, value: int | None = None, type: str | None = None, escape: bool = True, sep: Union[str, "TextEntity", "Template"] = "", enabled: bool | Any = True):
        self._value = value
        self._type = type
        super().__init__(*content, escape=escape, sep=sep, enabled=enabled)

    def _render_html(self, content: str) -> str:
        return f"<li{_attrs(value=self._value, type=self._type)}>{content}</li>"


class _RichList(RichEntity):
    _ordered = False

    def _render_content(self, parse_mode):
        if parse_mode == "html":
            return "".join(
                self._render_item(item, parse_mode) if isinstance(item, ListItem)
                else f"<li>{self._render_item(item, parse_mode)}</li>"
                for item in self._content
            )
        lines = []
        for index, item in enumerate(self._content, start=1):
            marker = f"{index}. " if self._ordered else "• "
            lines.append(self._escape(marker, parse_mode) + self._render_item(item, parse_mode))
        return "\n".join(lines)


class UnorderedList(_RichList):
    """
    ⚠️ Works only in Rich mode (``sender.set_rich_html(True)``).

    Bulleted list: ``<ul>``. Items are strings/entities or ``ListItem``.

    Example::

        UnorderedList("One", Bold("Two"), ListItem("Three"))
    """
    def _render_html(self, content: str) -> str:
        return f"<ul>{content}</ul>"


class OrderedList(_RichList):
    """
    ⚠️ Works only in Rich mode (``sender.set_rich_html(True)``).

    Numbered list: ``<ol>``.

    :param start: First number.
    :param type: ``"1"``, ``"a"``, ``"A"``, ``"i"`` or ``"I"``.
    :param reversed: Count backwards.
    """
    _ordered = True

    def __init__(self, *items, start: int | None = None, type: str | None = None, reversed: bool = False, escape: bool = True, enabled: bool | Any = True):
        self._start = start
        self._type = type
        self._reversed = reversed
        super().__init__(*items, escape=escape, enabled=enabled)

    def _render_html(self, content: str) -> str:
        attrs = _attrs(start=self._start, type=self._type, reversed=self._reversed)
        return f"<ol{attrs}>{content}</ol>"


# -- tables

class TableCell(RichEntity):
    """⚠️ Works only in Rich mode (``sender.set_rich_html(True)``).

    Table cell ``<td>`` / ``<th>`` (``header=True``). Cells may contain only inline formatting."""
    def __init__(self, *content, header: bool = False, colspan: int | None = None, rowspan: int | None = None, align: Literal["left", "center", "right"] | None = None, valign: Literal["top", "middle", "bottom"] | None = None, escape: bool = True, sep: Union[str, "TextEntity", "Template"] = "", enabled: bool | Any = True):
        self._header = header
        self._span = {"colspan": colspan, "rowspan": rowspan, "align": align, "valign": valign}
        super().__init__(*content, escape=escape, sep=sep, enabled=enabled)

    def _render_html(self, content: str) -> str:
        tag = "th" if self._header else "td"
        return f"<{tag}{_attrs(**self._span)}>{content}</{tag}>"


class Table(RichEntity):
    """
    ⚠️ Works only in Rich mode (``sender.set_rich_html(True)``).

    Table: ``<table>``. Each row is a list/tuple of cells (strings, entities or ``TableCell``).

    :param header: Render the first row as header cells.

    Example::

        Table(["Name", "Score"], ["Ann", "10"], ["Bob", "7"], header=True, bordered=True)
    """
    def __init__(self, *rows, header: bool = False, bordered: bool = False, striped: bool = False, caption: Union[str, "TextEntity", "Template", None] = None, escape: bool = True, enabled: bool | Any = True):
        self._header = header
        self._bordered = bordered
        self._striped = striped
        self._caption = caption
        super().__init__(*rows, escape=escape, enabled=enabled)

    def _render_content(self, parse_mode):
        is_html = parse_mode == "html"
        lines = []

        if self._caption is not None:
            caption = self._render_item(self._caption, parse_mode)
            lines.append(f"<caption>{caption}</caption>" if is_html else caption)

        for row_index, row in enumerate(self._content):
            cells = []
            for cell in row:
                rendered = self._render_item(cell, parse_mode)
                if is_html and not isinstance(cell, TableCell):
                    tag = "th" if (self._header and row_index == 0) else "td"
                    rendered = f"<{tag}>{rendered}</{tag}>"
                cells.append(rendered)

            if is_html:
                lines.append("<tr>" + "".join(cells) + "</tr>")
            else:
                lines.append(self._escape(" | ", parse_mode).join(cells))

        return ("" if is_html else "\n").join(lines)

    def _render_html(self, content: str) -> str:
        return f"<table{_attrs(bordered=self._bordered, striped=self._striped)}>{content}</table>"


# -- media (http/https URLs only)

class _RichMedia(RichEntity):
    def __init__(self, url: str, *, caption: Union[str, "TextEntity", "Template", None] = None, credit: Union[str, "TextEntity", "Template", None] = None, spoiler: bool = False, enabled: bool | Any = True):
        self._url = url
        self._caption = caption
        self._credit = credit
        self._spoiler = spoiler
        super().__init__(enabled=enabled)

    def _media(self) -> str:
        raise NotImplementedError

    def _render_html(self, content: str) -> str:
        media = self._media()
        if self._caption is None and self._credit is None:
            return media

        caption = self._render_item(self._caption, "html") if self._caption is not None else ""
        credit = f"<cite>{self._render_item(self._credit, 'html')}</cite>" if self._credit is not None else ""
        return f"<figure>{media}<figcaption>{caption}{credit}</figcaption></figure>"

    def _media_attrs(self) -> str:
        return _attrs(src=self._url, **{"tg-spoiler": self._spoiler})


class Image(_RichMedia):
    """⚠️ Works only in Rich mode (``sender.set_rich_html(True)``).

    Photo block: ``<img>``; with ``caption``/``credit`` it is wrapped into ``<figure>``."""
    def _media(self) -> str:
        return f"<img{self._media_attrs()}/>"


class Video(_RichMedia):
    """⚠️ Works only in Rich mode (``sender.set_rich_html(True)``).

    Video block: ``<video>``."""
    def _media(self) -> str:
        return f"<video{self._media_attrs()}></video>"


class Audio(_RichMedia):
    """⚠️ Works only in Rich mode (``sender.set_rich_html(True)``).

    Audio block: ``<audio>`` (.ogg is shown as a voice note)."""
    def _media(self) -> str:
        return f"<audio{self._media_attrs()}></audio>"


class Map(RichEntity):
    """⚠️ Works only in Rich mode (``sender.set_rich_html(True)``).

    Map block: ``<tg-map>``. ``zoom`` must be 13–20."""
    def __init__(self, lat: float, long: float, *, zoom: int = 15, enabled: bool | Any = True):
        if not 13 <= zoom <= 20:
            raise ValueError("Map zoom must be between 13 and 20")
        self._lat, self._long, self._zoom = lat, long, zoom
        super().__init__(enabled=enabled)

    def _render_html(self, content: str) -> str:
        return f"<tg-map{_attrs(lat=self._lat, long=self._long, zoom=self._zoom)}/>"


class Collage(RichEntity):
    """⚠️ Works only in Rich mode (``sender.set_rich_html(True)``).

    Collage of media blocks: ``<tg-collage>``. Pass ``Image``/``Video`` entities."""
    def _render_html(self, content: str) -> str:
        return f"<tg-collage>{content}</tg-collage>"


class Slideshow(RichEntity):
    """⚠️ Works only in Rich mode (``sender.set_rich_html(True)``).

    Slideshow of media blocks: ``<tg-slideshow>``."""
    def _render_html(self, content: str) -> str:
        return f"<tg-slideshow>{content}</tg-slideshow>"


class Styles:
    """
    Namespace for message formatting styles:

    >>> Styles.Bold("Hello").render("html")
    "<b>Hello</b>"
    >>> Styles.Bold("Hello").markdown
    "*Hello*"

    Pass it as a style object to the `sender`:
    >>> sender.set_text(Styles.Bold("Hello"))

    `Documentation <https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md>`_ · on GitHub
    """

    Bold: type[TextEntity] = Bold
    Italic: type[TextEntity] = Italic
    Underline: type[TextEntity] = Underline
    Strikethrough: type[TextEntity] = Strikethrough
    Code: type[TextEntity] = Code
    Python: type[TextEntity] = Python
    Spoiler: type[TextEntity] = Spoiler
    Quote: type[TextEntity] = Quote
    Sanitize: type[TextEntity] = Escape
    NoSanitize: type[TextEntity] = Raw
    Link: type[TextEntity] = Link
    Mention: type[TextEntity] = Mention
    UserLink: type[TextEntity] = UserLink
    BotLink: type[TextEntity] = BotLink
    Group: type[TextEntity] = Group
    # Rich HTML
    Marked: type[TextEntity] = Marked
    Subscript: type[TextEntity] = Subscript
    Superscript: type[TextEntity] = Superscript
    CustomEmoji: type[TextEntity] = CustomEmoji
    DateTime: type[TextEntity] = DateTime
    Math: type[TextEntity] = Math
    MathBlock: type[TextEntity] = MathBlock
    Anchor: type[TextEntity] = Anchor
    AnchorLink: type[TextEntity] = AnchorLink
    Reference: type[TextEntity] = Reference
    Heading: type[TextEntity] = Heading
    Paragraph: type[TextEntity] = Paragraph
    Footer: type[TextEntity] = Footer
    Divider: type[TextEntity] = Divider
    Cite: type[TextEntity] = Cite
    PullQuote: type[TextEntity] = PullQuote
    Details: type[TextEntity] = Details
    ListItem: type[TextEntity] = ListItem
    UnorderedList: type[TextEntity] = UnorderedList
    OrderedList: type[TextEntity] = OrderedList
    Table: type[TextEntity] = Table
    TableCell: type[TextEntity] = TableCell
    Image: type[TextEntity] = Image
    Video: type[TextEntity] = Video
    Audio: type[TextEntity] = Audio
    Map: type[TextEntity] = Map
    Collage: type[TextEntity] = Collage
    Slideshow: type[TextEntity] = Slideshow