# Copyright (c) 2025 Ving Studio, Romashka
# Licensed under the MIT License. See LICENSE file for full terms.

from urllib.parse import quote

from .formatter import StyleFormatter, Composite, sanitize_text


class Bold(StyleFormatter):
    markdown_symbol = ('*', '*')
    html_tag = ('<b>', '</b>')


class Italic(StyleFormatter):
    markdown_symbol = ('_', '_')
    html_tag = ('<i>', '</i>')


class Underline(StyleFormatter):
    markdown_symbol = ('__', '__')
    html_tag = ('<u>', '</u>')


class Strikethrough(StyleFormatter):
    markdown_symbol = ('~~', '~~')
    html_tag = ('<s>', '</s>')


class Code(StyleFormatter):
    markdown_symbol = ('`', '`')
    html_tag = ('<code>', '</code>')


class Python(StyleFormatter):
    markdown_symbol = ('```python', '\n```\n')
    html_tag = ('<pre language="python">', "\n</pre>\n")


class Spoiler(StyleFormatter):
    markdown_symbol = ('||', '||')
    html_tag = ('<span class="tg-spoiler">', '</span>')


class Quote(StyleFormatter):
    markdown_symbol = ('', '\n')
    html_tag = ('<blockquote>', '</blockquote>\n')

class Sanitize(StyleFormatter):
    markdown_symbol = ('', '')
    html_tag = ('', '')

class NoSanitize(StyleFormatter):
    markdown_symbol = ('', '')
    html_tag = ('', '')

    def render_markdown(self):
        return ''.join(
            c.render_markdown() if isinstance(c, StyleFormatter) else str(c)
            for c in self.content
        )

    def render_html(self):
        return ''.join(
            c.render_html() if isinstance(c, StyleFormatter) else str(c)
            for c in self.content
        )
    
class Link(StyleFormatter):
    markdown_symbol = ''
    html_tag = ''

    def __init__(self, *content, url: str, parse_mode: str | None = "html"):
        self.content = list(content)
        self.set_parse_mode(parse_mode)
        self.url = url

    def render_markdown(self):
        label = ''.join(
            c.render_markdown() if isinstance(c, StyleFormatter) else sanitize_text(str(c), "markdown")
            for c in self.content
        )
        return f"[{label}]({self.url})"

    def render_html(self):
        label = ''.join(
            c.render_html() if isinstance(c, StyleFormatter) else sanitize_text(str(c), "html")
            for c in self.content
        )
        return f'<a href="{self.url}">{label}</a>'
    
    def render_none(self):
        label = ''.join(
            c.render_none() if isinstance(c, StyleFormatter) else str(c)
            for c in self.content
        )
        return f"{label} ({self.url})"
    
class UserLink(Link):
    markdown_symbol = ''
    html_tag = ''

    def __init__(self, *content, username: str, text: str | None=None, parse_mode: str | None = "html"):
        self.content = list(content)
        self.set_parse_mode(parse_mode)

        if text is None:
            self.url = f"https://t.me/{username}"
        else:
            encoded_text = quote(text, safe="")
            self.url = f"https://t.me/{username}?text={encoded_text}"

class Styles:
    def __init__(self, parse_mode: str | None = "html"):
        self.parse_mode = parse_mode

    def use_markdown(self):
        self.parse_mode = "markdown"

    def use_html(self):
        self.parse_mode = "html"

    def set_parse_mode(self, parse_mode: str | None):
        self.parse_mode = parse_mode

    def bold(self, *content):
        return Bold(*content, parse_mode=self.parse_mode)

    def italic(self, *content):
        return Italic(*content, parse_mode=self.parse_mode)

    def underline(self, *content):
        return Underline(*content, parse_mode=self.parse_mode)

    def strike(self, *content):
        return Strikethrough(*content, parse_mode=self.parse_mode)

    def code(self, *content):
        return Code(*content, parse_mode=self.parse_mode)

    def python(self, *content):
        return Python(*content, parse_mode=self.parse_mode)

    def spoiler(self, *content):
        return Spoiler(*content, parse_mode=self.parse_mode)

    def quote(self, *content):
        return Quote(*content, parse_mode=self.parse_mode)
    
    def group(self, *content):
        return Composite(*content)
    
    def sanitize(self, *content):
        return Sanitize(*content, parse_mode=self.parse_mode)
    
    def no_sanitize(self, *content):
        return NoSanitize(*content, parse_mode=self.parse_mode)