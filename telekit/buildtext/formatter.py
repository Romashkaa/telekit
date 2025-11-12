# Copyright (c) 2025 Ving Studio, Romashka
# Licensed under the MIT License. See LICENSE file for full terms.

class StyleFormatter:
    markdown_symbol: str | tuple[str, str] = ''
    html_tag: str | tuple[str, str] = ''

    def __init__(self, *content, parse_mode: str = "html"):
        self.content = list(content)
        self.parse_mode = parse_mode

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
            c.render_markdown() if isinstance(c, StyleFormatter) else str(c)
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
            c.render_html() if isinstance(c, StyleFormatter) else str(c)
            for c in self.content
        )
        return f"{start}{body}{end}"
    
    def __str__(self) -> str:
        if self.parse_mode.lower() == "html":
            return self.html
        return self.markdown

    @property
    def markdown(self):
        return self.render_markdown()

    @property
    def html(self):
        return self.render_html()


class Composite(StyleFormatter):
    def __init__(self, *parts):
        super().__init__(parts)
        self.parts = parts

    def render_markdown(self):
        return ''.join(
            p.render_markdown() if isinstance(p, StyleFormatter) else str(p)
            for p in self.parts
        )

    def render_html(self):
        return ''.join(
            p.render_html() if isinstance(p, StyleFormatter) else str(p)
            for p in self.parts
        )