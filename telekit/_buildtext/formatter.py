# Copyright (c) 2025 Ving Studio, Romashka
# Licensed under the MIT License. See LICENSE file for full terms.

from html import escape

def sanitize_text(text: str, mode: str | None="html"):
    if not mode:
        return text

    if mode.lower() == "html":
        return escape(text)
    elif mode.lower() == "markdown":
        escape_chars = r"_*[]()~`>#+-=|{}.!"
        for c in escape_chars:
            text = text.replace(c, f"\\{c}")
        return text
    else:
        raise ValueError("Unknown mode, should be 'html' or 'markdown'")

class StyleFormatter:
    markdown_symbol: str | tuple[str, str] = ''
    html_tag: str | tuple[str, str] = ''

    def __init__(self, *content, parse_mode: str | None = "html"):
        self.content = list(content)
        self.set_parse_mode(parse_mode)

    def __add__(self, other):
        if isinstance(other, (str, StyleFormatter)):
            return Composite(self, other)
        raise TypeError(f"Cannot add {type(other)} to Style")

    def render_markdown(self):
        start, end = (
            self.markdown_symbol
            if isinstance(self.markdown_symbol, tuple)
            else (self.markdown_symbol, self.markdown_symbol)
        )

        body = ''.join(
            c.render_markdown() if isinstance(c, StyleFormatter) else sanitize_text(str(c), "markdown")
            for c in self.content
        )
        return f"{start}{body}{end}"

    def render_html(self):
        start, end = (
            self.html_tag
            if isinstance(self.html_tag, tuple)
            else (f"<{self.html_tag}>", f"</{self.html_tag}>")
        )

        body = ''.join(
            c.render_html() if isinstance(c, StyleFormatter) else sanitize_text(str(c), "html")
            for c in self.content
        )
        return f"{start}{body}{end}"
    
    def render_none(self):
        body = ''.join(
            c.render_none() if isinstance(c, StyleFormatter) else str(c)
            for c in self.content
        )
        return body
    
    def __str__(self) -> str:
        if self.parse_mode is None:
            return self.render_none()
        if self.parse_mode.lower() == "html":
            return self.render_html()
        return self.render_markdown()

    @property
    def markdown(self):
        return self.render_markdown()

    @property
    def html(self):
        return self.render_html()
    
    @property
    def none(self):
        return self.render_none()
    
    def set_parse_mode(self, parse_mode: str | None="html"):
        if parse_mode is None:
            self.parse_mode = None
        else:
            self.parse_mode = parse_mode.lower()


class Composite(StyleFormatter):
    def __init__(self, *parts):
        super().__init__(parts)
        self.parts = parts

    def render_markdown(self):
        return ''.join(
            p.render_markdown() if isinstance(p, StyleFormatter) else sanitize_text(str(p), "markdown")
            for p in self.parts
        )

    def render_html(self):
        return ''.join(
            p.render_html() if isinstance(p, StyleFormatter) else sanitize_text(str(p), "html")
            for p in self.parts
        )
    
    def render_none(self):
        return ''.join(
            p.render_none() if isinstance(p, StyleFormatter) else str(p)
            for p in self.parts
        )