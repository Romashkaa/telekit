# Copyright (c) 2025 Ving Studio, Romashka
# Licensed under the MIT License. See LICENSE file for full terms.

from .formatter import StyleFormatter


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
    markdown_symbol = ('\n```python', '\n```\n')
    html_tag = ('\n<pre language="python">', "\n</pre>\n")


class Spoiler(StyleFormatter):
    markdown_symbol = ('||', '||')
    html_tag = ('<span class="tg-spoiler">', '</span>')


class Quote(StyleFormatter):
    markdown_symbol = ('\n', '\n')
    html_tag = ('\n<blockquote>', '</blockquote>\n')

class Styles:
    def __init__(self, parse_mode: str = "html"):
        self.parse_mode = parse_mode

    def use_markdown(self):
        self.parse_mode = "markdown"

    def use_html(self):
        self.parse_mode = "html"

    def set_parse_mode(self, parse_mode: str):
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