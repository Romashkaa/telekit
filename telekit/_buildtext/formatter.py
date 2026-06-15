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

import sys
from typing import Any, Literal, TYPE_CHECKING, Union

import telebot.formatting

if TYPE_CHECKING: 
    from string.templatelib import Template, Interpolation # pyright: ignore[reportMissingImports]

_HAS_TEMPLATE_LIB = sys.version_info >= (3, 14)

if _HAS_TEMPLATE_LIB:
    from string.templatelib import Template as _Template # pyright: ignore[reportMissingImports]
else:
    _Template = None

class TextEntity:

    def __init__(self, *content, escape: bool = True, sep: Union["TextEntity", str, "Template"] = ""):
        self._content = content
        self._escape_strings = escape
        self._separator = sep

    def __add__(self, other):
        if isinstance(other, (str, TextEntity)) \
        or (_HAS_TEMPLATE_LIB and isinstance(other, _Template)): # pyright: ignore[reportArgumentType]
            return Group(self, other)
        raise TypeError(f"Cannot add {type(other)} to Style")

    @property
    def markdown(self) -> str:
        return self.render_markdown()

    @property
    def html(self) -> str:
        return self.render_html()
    
    @property
    def none(self) -> str:
        return self.render_none()
    
    def render_markdown(self) -> str:
        return self._render_content("markdown")

    def render_html(self) -> str:
        return self._render_content("html")
    
    def render_none(self) -> str:
        return self._render_content(None)
    
    def render(self, parse_mode: Literal["html", "markdown"] | None) -> str:
        match parse_mode:
            case "html":
                return self.render_html()
            case "markdown":
                return self.render_markdown()
            case _:
                return self.render_none()
    
    def _render_content(self, parse_mode: Literal["html", "markdown"] | None) -> str:
        sep: str = self._render_item(self._separator, parse_mode)

        return sep.join(
            self._render_item(item, parse_mode) for item in self._content
        )
    
    def _render_item(self, item: Union[str, "TextEntity", "Template"], parse_mode: Literal["html", "markdown"] | None) -> str:
        if _HAS_TEMPLATE_LIB and isinstance(item, _Template): # pyright: ignore[reportArgumentType]
            return self._render_template(item, parse_mode)    # pyright: ignore[reportAttributeAccessIssue]
        if isinstance(item, TextEntity):
            return item.render(parse_mode)
        return self._maybe_escape(item, parse_mode)
    
    def _render_template(self, template: "Template", parse_mode: Literal["html", "markdown"] | None) -> str:
        """
        Unwraps a Template (t-string) into a Group: static text chunks
        go through normal escaping, while interpolations are either
        rendered as nested TextEntity objects or escaped as values.
        """
        parts: list[Any] = []

        for piece in template:
            if isinstance(piece, str):
                # static text between {...}
                parts.append(piece)
            else:
                # Interpolation
                value = piece.value

                if isinstance(value, TextEntity) or (_HAS_TEMPLATE_LIB and isinstance(value, _Template)): # pyright: ignore[reportArgumentType]
                    parts.append(value)
                else:
                    # apply !r / !s / !a conversion if specified
                    if piece.conversion == "r":
                        value = repr(value)
                    elif piece.conversion == "s":
                        value = str(value)
                    elif piece.conversion == "a":
                        value = ascii(value)

                    # apply format_spec if specified
                    if piece.format_spec:
                        value = format(value, piece.format_spec)

                    parts.append(value)

        return Group(*parts, escape=self._escape_strings).render(parse_mode)
    
    def _maybe_escape(self, item: Any, parse_mode: Literal["html", "markdown"] | None) -> str:
        if self._escape_strings:
            return self._escape(item, parse_mode)
        else:
            return str(item)
        
    def _escape(self, text: Any, parse_mode: Literal["html", "markdown"] | None) -> str:
        text = str(text)

        match parse_mode:
            case "html":
                return telebot.formatting.escape_html(text)
            case "markdown":
                return telebot.formatting.escape_markdown(text)
            case _:
                return text
            
    def debug(self, parse_mode: Literal["html", "markdown"] | None="html", label: str | None = None) -> None:
        """
        Print a formatted debug representation of the current style to the console.

        Renders the style using the specified parse mode and displays it
        with a labeled separator via ``debug_style()``.

        :param parse_mode: Parse mode to use for rendering — ``"html"``, ``"markdown"``, or ``None`` for plain text.
        :type parse_mode: ``Literal["html", "markdown"] | None``
        :param label: Optional label shown in the debug header.
        :type label: ``str | None``

        Example::

            >>> Bold("Hello").debug("html", label="test")
            ––––––– test Parse Mode: html –––––––

            <b>Hello</b>
        """
        debug_style(self, label=label, parse_mode=parse_mode)
            
class EasyTextEntity(TextEntity):
    def render_markdown(self) -> str:
        return self._render_markdown(self._render_content("markdown"))

    def render_html(self) -> str:
        return self._render_html(self._render_content("html"))
    
    def render_none(self) -> str:
        return self._render_none(self._render_content(None))
    
    # redefine

    def _render_markdown(self, content: str) -> str:
        return content

    def _render_html(self, content: str) -> str:
        return content
    
    def _render_none(self, content: str) -> str:
        return content
    
class EasyTextEntityWithPostRender(EasyTextEntity):
    def render_markdown(self) -> str:
        return self._post_render(self._render_markdown(self._render_content("markdown")))

    def render_html(self) -> str:
        return self._post_render(self._render_html(self._render_content("html")))
    
    def render_none(self) -> str:
        return self._post_render(self._render_none(self._render_content(None)))
    
    # redefine

    def _post_render(self, rendered: str) -> str:
        return rendered
    
    # + _render_markdown, _render_html, _render_none
    
class StaticTextEntity(TextEntity):
    def render_markdown(self) -> str:
        content: str = self._render_content("markdown")
        return self._render_any(content)

    def render_html(self) -> str:
        content: str = self._render_content("html")
        return self._render_any(content)
    
    def render_none(self) -> str:
        content: str = self._render_content(None)
        return self._render_any(content)
    
    # redefine

    def _render_any(self, content: str) -> str:
        return content

# Grouping

class Group(TextEntity):
    def __init__(self, *content, escape: bool = True, sep: Union[str, "TextEntity", "Template"] = ""):
        super().__init__(*content, escape=escape, sep=sep)

# Debugger

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

def debug_style(*args, parse_mode: Literal["html", "markdown"] | None, label: str | None=None, sep: str="\n"):
    _desc: str = f" {label}" if label else ""
    text: str = Group(*args, sep=sep).render(parse_mode)

    print(f"–––––––{_desc} Parse Mode: {parse_mode} –––––––", end="\n\n")
    RichPrinter.print_using_rich(text, parse_mode)
    print()