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

from .formatter import StyleFormatter, StyleFormatter2, StyleFormatter3, Group


class Bold(StyleFormatter2):

    def _render_markdown(self, content: str) -> str:
        return f"*{content}*"

    def _render_html(self, content: str) -> str:
        return f"<b>{content}</b>"


class Italic(StyleFormatter2):

    def _render_markdown(self, content: str) -> str:
        return f"_{content}_"

    def _render_html(self, content: str) -> str:
        return f"<i>{content}</i>"


class Underline(StyleFormatter2):

    def _render_markdown(self, content: str) -> str:
        return f"__{content}__"

    def _render_html(self, content: str) -> str:
        return f"<u>{content}</u>"


class Strikethrough(StyleFormatter2):

    def _render_markdown(self, content: str) -> str:
        return f"~~{content}~~"

    def _render_html(self, content: str) -> str:
        return f"<s>{content}</s>"


class Code(StyleFormatter2):

    def _render_markdown(self, content: str) -> str:
        return f"`{content}`"

    def _render_html(self, content: str) -> str:
        return f"<code>{content}</code>"


class Python(StyleFormatter2):

    def _render_markdown(self, content: str) -> str:
        return f"```{content}```"

    def _render_html(self, content: str) -> str:
        return f'<pre language="python">{content}\n</pre>\n'


class Spoiler(StyleFormatter2):

    def _render_markdown(self, content: str) -> str:
        return f"||{content}||"

    def _render_html(self, content: str) -> str:
        # or '<span class="tg-spoiler">', '</span>'
        return f'<tg-spoiler>{content}</tg-spoiler>'


class Quote(StyleFormatter2):

    def __init__(self, *content, expandable: bool = False, escape: bool = True, sep: Union["StyleFormatter", str] = ""):
        self.expandable: bool = expandable
        super().__init__(*content, escape=escape, sep=sep)

    def _render_markdown(self, content: str) -> str:
        return telebot.formatting.mcite(content, expandable=self.expandable)

    def _render_html(self, content: str) -> str:
        return telebot.formatting.hcite(content, expandable=self.expandable)


class Escape(StyleFormatter):

    def __init__(self, *content, sep: Union["StyleFormatter", str] = ""):
        super().__init__(*content, escape=True, sep=sep)


class Raw(StyleFormatter):
    
    def __init__(self, *content, sep: Union["StyleFormatter", str] = ""):
        super().__init__(*content, escape=False, sep=sep)
    

class Link(StyleFormatter2):

    def __init__(self, *content, url: str, escape: bool = True, sep: Union["StyleFormatter", str] = ""):
        self._url: str = url
        super().__init__(*content, escape=escape, sep=sep)

    def _render_markdown(self, content: str) -> str:
        return f"[{content}]({self._url})"

    def _render_html(self, content: str) -> str:
        return f'<a href="{self._url}">{content}</a>'
    
    def _render_none(self, content: str) -> str:
        return f"{content} ({self._url})"
    

class UserLink(Link):
    def __init__(self, *content, username: str, text: str | None=None, escape: bool = True, sep: Union["StyleFormatter", str] = ""):
        username = username.lstrip("@")

        if text is None:
            url: str = f"https://t.me/{username}"
        else:
            encoded_text: str = quote(text, safe="")
            url: str = f"https://t.me/{username}?text={encoded_text}"

        super().__init__(*content, url=url, escape=escape, sep=sep)


class BotLink(Link):
    def __init__(self, *content, username: str, start: str | None=None, escape: bool = True, sep: Union["StyleFormatter", str] = ""):
        username = username.lstrip("@")

        if start is None:
            url: str = f"https://t.me/{username}"
        else:
            encoded_start = quote(start, safe="")
            url: str = f"https://t.me/{username}?start={encoded_start}"

        super().__init__(*content, url=url, escape=escape, sep=sep)

class EncodeHTML(StyleFormatter3):

    def _render_any(self, content: str) -> str:
        return quote(content, safe="")


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

    Bold: type[StyleFormatter] = Bold
    Italic: type[StyleFormatter] = Italic
    Underline: type[StyleFormatter] = Underline
    Strikethrough: type[StyleFormatter] = Strikethrough
    Code: type[StyleFormatter] = Code
    Python: type[StyleFormatter] = Python
    Spoiler: type[StyleFormatter] = Spoiler
    Quote: type[StyleFormatter] = Quote
    Sanitize: type[StyleFormatter] = Escape
    NoSanitize: type[StyleFormatter] = Raw
    Link: type[StyleFormatter] = Link
    UserLink: type[StyleFormatter] = UserLink
    BotLink: type[StyleFormatter] = BotLink
    Group: type[StyleFormatter] = Group

class RichPrinter():
    @classmethod
    def print_using_rich(cls, text: str, parse_mode: Literal["html", "markdown"] | None):
        cls._try_install_rich()

        if parse_mode is not None and cls._rich_is_installed():
            syntax = cls._rich_syntax(text, parse_mode, theme="monokai")
            cls._rich_console.print(syntax)
        else:
            print(text)

    @classmethod
    def _rich_is_installed(cls):
        return hasattr(cls, "_rich_console") and hasattr(cls, "_rich_syntax")
        
    @classmethod
    def _try_install_rich(cls):
        if cls._rich_is_installed():
            return
        
        try:
            import rich
            from rich.syntax import Syntax

            cls._rich_syntax = Syntax
            cls._rich_console = rich.console.Console()
        except:
            print("\n * Install 'rich' to highlight the syntax")

def debug_style(*args, parse_mode: Literal["html", "markdown"] | None, desc: str | None=None, sep: str="\n"):
    _desc: str = f" {desc}" if desc else ""
    text: str = Group(*args, sep=sep).render(parse_mode)

    print(f"–––––––{_desc} Parse Mode: {parse_mode} –––––––", end="\n\n")
    RichPrinter.print_using_rich(text, parse_mode)
    print()


    