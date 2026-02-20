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
from enum import Enum
from urllib.parse import quote

import telebot.formatting

from .formatter import TextEntity, EasyTextEntity, StaticTextEntity, EasyTextEntityWithPostRender, Group


class Bold(EasyTextEntity):

    def _render_markdown(self, content: str) -> str:
        return f"*{content}*"

    def _render_html(self, content: str) -> str:
        return f"<b>{content}</b>"


class Italic(EasyTextEntity):

    def _render_markdown(self, content: str) -> str:
        return f"_{content}_" # TODO add "\r"

    def _render_html(self, content: str) -> str:
        return f"<i>{content}</i>"


class Underline(EasyTextEntity):

    def _render_markdown(self, content: str) -> str:
        return f"__{content}__"

    def _render_html(self, content: str) -> str:
        return f"<u>{content}</u>"


class Strikethrough(EasyTextEntity):

    def _render_markdown(self, content: str) -> str:
        return f"~~{content}~~"

    def _render_html(self, content: str) -> str:
        return f"<s>{content}</s>"


class Code(EasyTextEntity):

    def _render_markdown(self, content: str) -> str:
        return f"`{content}`"

    def _render_html(self, content: str) -> str:
        return f"<code>{content}</code>"
    

class Language(EasyTextEntity):

    def __init__(self, *content, lang: str, escape: bool = True, sep: Union["TextEntity", str] = ""):
        self._language: str = lang
        super().__init__(*content, escape=escape, sep=sep)

    def _render_markdown(self, content: str) -> str:
        return f"```{self._language}\n{content}```"

    def _render_html(self, content: str) -> str:
        return f'<pre language="{self._language}">{content}\n</pre>\n'


class Python(Language):

    def __init__(self, *content, escape: bool = True, sep: Union["TextEntity", str] = ""):
        super().__init__(*content, lang="python", escape=escape, sep=sep)


class Spoiler(EasyTextEntity):

    def _render_markdown(self, content: str) -> str:
        return f"||{content}||"

    def _render_html(self, content: str) -> str:
        # or '<span class="tg-spoiler">', '</span>'
        return f'<tg-spoiler>{content}</tg-spoiler>'


class Quote(EasyTextEntityWithPostRender):

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

    def __init__(self, *content, sep: Union["TextEntity", str] = ""):
        super().__init__(*content, escape=True, sep=sep)


class Raw(TextEntity):
    
    def __init__(self, *content, sep: Union["TextEntity", str] = ""):
        super().__init__(*content, escape=False, sep=sep)
    

class Link(EasyTextEntity):

    def __init__(self, *content, url: str, escape: bool = True, sep: Union["TextEntity", str] = ""):
        self._url: str = url
        super().__init__(*content, escape=escape, sep=sep)

    def _render_markdown(self, content: str) -> str:
        return f"[{content}]({self._url})"

    def _render_html(self, content: str) -> str:
        return f'<a href="{self._url}">{content}</a>'
    
    def _render_none(self, content: str) -> str:
        return f"{content} ({self._url})"
    

class UserLink(Link):
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

class EncodeHTML(StaticTextEntity):

    def _render_any(self, content: str) -> str:
        return quote(content, safe="")
    
class Stack(TextEntity):

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
    UserLink: type[TextEntity] = UserLink
    BotLink: type[TextEntity] = BotLink
    Group: type[TextEntity] = Group

class RichPrinter():

    @classmethod
    def print_using_rich(cls, text: str, parse_mode: Literal["html", "markdown"] | None):
        cls._try_install_rich()
        
        if parse_mode is not None and cls._rich_is_installed():
            syntax = cls._rich_syntax(text, parse_mode, theme="material")
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


    