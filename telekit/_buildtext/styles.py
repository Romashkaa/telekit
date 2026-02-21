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
from typing import Union, Literal
from urllib.parse import quote

import telebot.formatting

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

    Examples::

        Bold("Hello").html      # "<b>Hello</b>"
        Bold("Hello").markdown  # "*Hello*"

        Bold("Hello", "World", sep=" ").html  # "<b>Hello World</b>"

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

    Examples::

        Language("x = 1", lang="python").markdown
        # "```python\\nx = 1```"

        Language("console.log(1)", lang="javascript").html
        # '<pre language="javascript">console.log(1)\\n</pre>\\n'

        sender.set_text(Language("x = 1", lang="python"))

    `Documentation <https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md>`_ · on GitHub
    """

    def __init__(self, *content, lang: str, escape: bool = True, sep: Union["TextEntity", str] = ""):
        self._language: str = lang
        super().__init__(*content, escape=escape, sep=sep)

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

    Examples::

        Python("x = 1").markdown  # "```python\\nx = 1```"
        Python("x = 1").html      # '<pre language="python">x = 1\\n</pre>\\n'

        sender.set_text(Python("def hello(): pass"))

    `Documentation <https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md>`_ · on GitHub
    """

    def __init__(self, *content, escape: bool = True, sep: Union["TextEntity", str] = ""):
        super().__init__(*content, lang="python", escape=escape, sep=sep)


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

    Examples::

        Spoiler("secret").html      # "<tg-spoiler>secret</tg-spoiler>"
        Spoiler("secret").markdown  # "||secret||"

        sender.set_text(Spoiler("plot twist"))

    `Documentation <https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md>`_ · on GitHub
    """

    def _render_markdown(self, content: str) -> str:
        return telebot.formatting.mspoiler(content, escape=False)

    def _render_html(self, content: str) -> str:
        # or '<span class="tg-spoiler">', '</span>'
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

    Examples::

        Quote("Be yourself.").html
        # "<blockquote>Be yourself.</blockquote>\\n"

        Quote("Very long text...", expandable=True).html
        # expandable blockquote

        sender.set_text(Quote("Note: this is important"))

    `Documentation <https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md>`_ · on GitHub
    """

    def __init__(self, *content, expandable: bool = False, end: str = "\n", escape: bool = True, sep: Union["TextEntity", str] = ""):
        self._expandable: bool = expandable
        self._end: str = end
        super().__init__(*content, escape=escape, sep=sep)

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

    def __init__(self, *content, sep: Union["TextEntity", str] = ""):
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
    
    def __init__(self, *content, sep: Union["TextEntity", str] = ""):
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

    def __init__(self, *content, url: str, escape: bool = True, sep: Union["TextEntity", str] = ""):
        self._url: str = url
        super().__init__(*content, escape=escape, sep=sep)

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

    Examples::

        Mention("John", user_id=123456789).html
        # '<a href="tg://user?id=123456789">John</a>'

        Mention("John", user_id=123456789).markdown
        # "[John](tg://user?id=123456789)"

        sender.set_text(Mention(user.first_name, user_id=user.id))

    `Documentation <https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md>`_ · on GitHub
    """

    def __init__(self, *content, user_id: int, escape: bool = True, sep: Union["TextEntity", str] = ""):
        url: str = self.gen_link(user_id)
        super().__init__(*content, url=url, escape=escape, sep=sep)

    @staticmethod
    def gen_link(user_id: int) -> str:
        return f"tg://user?id={user_id}"
    

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

    Examples::

        UserLink("Contact support", username="support_manager").html
        # '<a href="https://t.me/support_manager">Contact support</a>'

        UserLink("Say hi", username="john2004", text="Hello!").html
        # '<a href="https://t.me/john2004?text=Hello%21">Say hi</a>'

    `Documentation <https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md>`_ · on GitHub
    """
    def __init__(self, *content, username: str, text: str | None = None, escape: bool = True, sep: Union["TextEntity", str] = ""):
        url: str = self.gen_link(username, text)

        super().__init__(*content, url=url, escape=escape, sep=sep)

    @staticmethod
    def gen_link(username: str, text: str | None = None) -> str:
        username = username.lstrip("@")

        if text is None:
            return f"https://t.me/{username}"
        else:
            encoded_text: str = quote(text, safe="")
            return f"https://t.me/{username}?text={encoded_text}"


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

    Examples::

        BotLink("Open bot", username="my_bot").html
        # '<a href="https://t.me/my_bot">Open bot</a>'

        BotLink("Get started", username="my_bot", start="ref_123").html
        # '<a href="https://t.me/my_bot?start=ref_123">Get started</a>'

    `Documentation <https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md>`_ · on GitHub
    """
    
    def __init__(self, *content, username: str, start: str | None = None, escape: bool = True, sep: Union["TextEntity", str] = ""):
        url: str = self.gen_link(username, start)

        super().__init__(*content, url=url, escape=escape, sep=sep)

    @staticmethod
    def gen_link(username: str, start: str | None = None) -> str:
        username = username.lstrip("@")

        if start is None:
            return f"https://t.me/{username}"
        else:
            encoded_start = quote(start, safe="")
            return f"https://t.me/{username}?start={encoded_start}"

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
            ```
            \"""
            - 1. A
            - 2. B
            \"""
            ```

            >>> Stack("A", "B", start=Stack.Markers.DOT).html
            ```
            \"""
            • A
            • B
            \"""
            ```

    :param sep: Separator appended at the end of each item except the last.
        Defaults to ``"\\n"``.

        Example::

            >>> Stack("A", "B", "C", sep=";\\n").html
            ```
            \"""
            1. A;
            2. B;
            3. C
            \"""
            ```

    :param end: Appended after the last item, e.g. a closing punctuation mark.
        Defaults to ``""``.

        Example::

            >>> Stack("A", "B", end=".").none
            ```
            \"""
            1. A
            2. B.
            \"""
            ```

    :param escape: Whether to escape HTML/Markdown special characters in plain string content.
        Defaults to ``True``.

    Examples::

        Stack("Buy milk", "Walk the dog", "Read a book").html
        ```
        \"""
        1. Buy milk
        2. Walk the dog
        3. Read a book
        \"""
        ```

        Stack("Buy milk", "Walk the dog", start=Stack.Markers.CHECK).html
        ```
        \"""
        ✓ Buy milk
        ✓ Walk the dog
        \"""
        ```

        Stack("Step one", "Step two", sep=";\\n", end=".").html
        ```
        \"""
        1. Step one;
        2. Step two.
        \"""
        ```

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

    def __init__(self, *content, start: str = "{{index}}. ", sep: Union["TextEntity", str] = "\n", end: Union["TextEntity", str] = "", escape: bool = True):
        self._start = start
        self._end = end

        super().__init__(*content, escape=escape, sep=sep)

    def _render_content(self, parse_mode: None | Literal['html'] | Literal['markdown']) -> str:
        stack: list[str] = []

        for index, item in enumerate(self._content, start=1):
            stack.append(
                self._start.replace("{{index}}", str(index)) + \
                self._render_item(item, parse_mode)
            )

        sep: str = self._render_item(self._separator, parse_mode)
        end: str = self._render_item(self._end, parse_mode)

        return "\n" + sep.join(stack) + end + "\n"

class Styles:

    """
    Namespace for message formatting styles:

    >>> Styles.Bold("Hello").render("html")
    "<b>Hello</b>"
    >>> Styles.Bold("Hello").markdown
    "*Hello*"

    Pass it as a style object to the `sender`:
    >>> sender.set_text(Styles.Bold("Hello"))
    
    [Documentation](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md) · on GitHub
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


    