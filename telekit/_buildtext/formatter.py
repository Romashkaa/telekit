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

from typing import Any, Literal, Union

import telebot.formatting

# def escape_text(text: Any, parse_mode: Literal["html", "markdown"] | None = "html"):
#     text = str(text)

#     match parse_mode:
#         case "html":
#             return telebot.formatting.escape_html(text)
#         case "markdown":
#             return telebot.formatting.escape_markdown(text)
#         case _:
#             return text

class StyleFormatter:

    def __init__(self, *content, escape: bool = True, sep: Union["StyleFormatter", str]=""):
        self._content = content
        self._escape_strings = escape
        self._separator = sep

    def __add__(self, other):
        if isinstance(other, (str, StyleFormatter)):
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
    
    def _render_item(self, item: Union[str, "StyleFormatter"], parse_mode: Literal["html", "markdown"] | None) -> str:
        if isinstance(item, StyleFormatter):
            return item.render(parse_mode)
        else:
            return self._maybe_escape(item, parse_mode)
    
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
            
class StyleFormatter2(StyleFormatter):
    def render_markdown(self) -> str:
        content: str = self._render_content("markdown")
        return self._render_markdown(content)

    def render_html(self) -> str:
        content: str = self._render_content("html")
        return self._render_html(content)
    
    def render_none(self) -> str:
        content: str = self._render_content(None)
        return self._render_none(content)
    
    # redefine

    def _render_markdown(self, content: str) -> str:
        return content

    def _render_html(self, content: str) -> str:
        return content
    
    def _render_none(self, content: str) -> str:
        return content
    
class StyleFormatter3(StyleFormatter):
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

class Group(StyleFormatter):
    def __init__(self, *content, escape: bool = True, sep: Union["StyleFormatter", str] = ""):
        super().__init__(*content, escape=escape, sep=sep)
