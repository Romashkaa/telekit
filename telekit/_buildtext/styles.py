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
    def __init__(self, *content, username: str, text: str | None=None, parse_mode: str | None = "html"):
        self.content = list(content)
        self.set_parse_mode(parse_mode)

        username = username.lstrip("@")

        if text is None:
            self.url = f"https://t.me/{username}"
        else:
            encoded_text = quote(text, safe="")
            self.url = f"https://t.me/{username}?text={encoded_text}"

class BotLink(Link):
    def __init__(self, *content, username: str, start: str | None=None, parse_mode: str | None = "html"):
        self.content = list(content)
        self.set_parse_mode(parse_mode)

        username = username.lstrip("@")

        if start is None:
            self.url = f"https://t.me/{username}"
        else:
            encoded_start = quote(start, safe="")
            self.url = f"https://t.me/{username}?start={encoded_start}"

class Styles:

    """
    Factory for message formatting styles with a shared `parse_mode`.

    Allows defining the parsing mode once and applying it consistently
    to all created styled objects:

    >>> styles = Styles("html")
    >>> styles.bold("hello")

    Can also be used as a namespace:

    >>> Styles.Bold("Hello!")
    >>> Styles.Bold("Hello!", parse_mode="html") 
    
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
    Sanitize: type[StyleFormatter] = Sanitize
    NoSanitize: type[StyleFormatter] = NoSanitize
    Link: type[StyleFormatter] = Link
    UserLink: type[StyleFormatter] = UserLink
    BotLink: type[StyleFormatter] = BotLink
    
    def __init__(self, parse_mode: str | None = "html"):
        self.parse_mode = parse_mode

    def use_markdown(self):
        """
        Switches parse_mode to Markdown for all subsequent styles. 
        >>> styles = Styles("html")
        >>> styles.bold("hello") 
        
        [Documentation](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md) · on GitHub
        """
        self.parse_mode = "markdown"

    def use_html(self):
        """
        Switches parse_mode to HTML for all subsequent styles. 
        >>> styles = Styles("html")
        >>> styles.bold("hello") 
        
        [Documentation](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md) · on GitHub
        """
        self.parse_mode = "html"
    
    def use_plain(self):
        """
        Disables formatting by setting parse_mode to None,
        resulting in plain text output without styles. 
        >>> styles = Styles("html")
        >>> styles.bold("hello") 
        
        [Documentation](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md) · on GitHub
        """
        self.parse_mode = None

    def set_parse_mode(self, parse_mode: str | None):
        """
        Explicitly sets the parse_mode used by all style methods
        of this object. 
        >>> styles = Styles("html")
        >>> styles.bold("hello") 
        
        [Documentation](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md) · on GitHub
        """
        self.parse_mode = parse_mode

    def bold(self, *content):
        """
        Applies **bold formatting** to the provided content. 
        
        [Documentation](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md) · on GitHub
        """
        return Bold(*content, parse_mode=self.parse_mode)

    def italic(self, *content):
        """
        Applies *italic formatting* to the provided content. 
        
        [Documentation](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md) · on GitHub
        """
        return Italic(*content, parse_mode=self.parse_mode)

    def underline(self, *content):
        """
        Applies underline formatting to the provided content. 
        
        [Documentation](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md) · on GitHub
        """
        return Underline(*content, parse_mode=self.parse_mode)

    def strike(self, *content):
        """
        Applies strikethrough formatting to the provided content. 
        
        [Documentation](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md) · on GitHub
        """
        return Strikethrough(*content, parse_mode=self.parse_mode)

    def code(self, *content):
        """
        Formats the content as inline monospace code. 
        
        [Documentation](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md) · on GitHub
        """
        return Code(*content, parse_mode=self.parse_mode)

    def python(self, *content):
        """
        Formats the content as a Python code block,
        with syntax highlighting. 
        
        [Documentation](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md) · on GitHub
        """
        return Python(*content, parse_mode=self.parse_mode)

    def spoiler(self, *content):
        """
        Hides the content behind a spoiler that can be revealed by the user. 
        
        [Documentation](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md) · on GitHub
        """
        return Spoiler(*content, parse_mode=self.parse_mode)

    def quote(self, *content):
        """
        Formats the content as a quoted message block. 
        
        [Documentation](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md) · on GitHub
        """
        return Quote(*content, parse_mode=self.parse_mode)
    
    def group(self, *content):
        """
        Combines multiple styled elements into a composite group
        without modifying parse_mode. 
        
        [Documentation](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md) · on GitHub
        """
        return Composite(*content)
    
    def sanitize(self, *content):
        """
        Escapes special characters according to parse_mode,
        making the text safe for rendering. 
        
        [Documentation](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md) · on GitHub
        """
        return Sanitize(*content, parse_mode=self.parse_mode)
    
    def no_sanitize(self, *content):
        """
        Passes content without escaping special characters,
        even when parse_mode is active. 
        
        [Documentation](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md) · on GitHub
        """
        return NoSanitize(*content, parse_mode=self.parse_mode)
    
    def link(self, *content, url: str):
        """
        Creates a clickable hyperlink from the content
        pointing to the specified URL. 
        
        [Documentation](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md) · on GitHub
        """
        return Link(*content, url=url, parse_mode=self.parse_mode)
    
    def user_link(self, *content, username: str, text: str | None=None):
        """
        Creates a Telegram user link by username,
        with optional custom display text. 
        
        [Documentation](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md) · on GitHub
        """
        return UserLink(*content, username=username, text=text, parse_mode=self.parse_mode)

    def bot_link(self, *content, username: str, start: str | None=None):
        """
        Creates a Telegram bot deep link with an optional start parameter,
        allowing data to be passed when opening the bot. 
        
        [Documentation](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md) · on GitHub
        """
        return BotLink(*content, username=username, start=start, parse_mode=self.parse_mode)