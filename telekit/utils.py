import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent  # telekit/


def format_file_size(size: int, precision: int = 1) -> str:
    """
    Convert a file size in bytes to a human-readable string using
    the binary unit system (1 KB = 1024 bytes).

    The function automatically selects the appropriate unit
    (B, KB, MB, GB, TB, PB) and formats the number according
    to the specified precision. Trailing zeros are removed.

    :param size: File size in bytes. Must be a non-negative integer.
    :type size: `int`

    :param precision: Number of decimal places to keep for fractional
        values. Ignored if the value is an integer after conversion.
        Default is 1.
    :type precision: `int`

    :raises ValueError: If ``size`` is negative.

    :return: Human-readable file size string.
    :rtype: `str`

    Examples:

    Basic usage:
        >>> format_file_size(500)
        '500 B'

        >>> format_file_size(2048)
        '2 KB'

        >>> format_file_size(1048576)
        '1 MB'

    Using precision:
        >>> format_file_size(1545, precision=2)
        '1.51 KB'

        >>> format_file_size(1600, precision=3)
        '1.562 KB'

        >>> format_file_size(123456789, precision=1)
        '117.7 MB'

    Large values:
        >>> format_file_size(1099511627776)
        '1 TB'
    """

    _size: int | float = size

    if _size < 0:
        raise ValueError("Size must be non-negative")

    units = ["B", "KB", "MB", "GB", "TB", "PB"]

    if _size == 0:
        return "0 B"

    index = 0
    _size = float(_size)

    while _size >= 1024 and index < len(units) - 1:
        _size /= 1024
        index += 1

    if _size.is_integer():
        formatted = f"{int(_size)}"
    else:
        formatted = f"{_size:.{precision}f}".rstrip("0").rstrip(".")

    return f"{formatted} {units[index]}"

def read_token(path: str = "token.txt") -> str:
    """
    Read the bot token from a file.

    Reads only the first line, so multiple tokens can be stored in the file
    and swapped quickly by reordering lines — no need to delete or copy.

    Inline comments are supported — everything after the first whitespace
    is ignored::

        123456789:BotSecretToken  Main production bot
        987654321:AnotherToken    Backup bot

    :param path: Path to the token file
    :type path: ``str``
    :return: Bot token string
    :rtype: ``str``
    """
    with open(path) as f:
        first_line: str = f.readline().strip()
        token, *_ = first_line.split()
        return token


def read_canvas_path(path: str = "canvas_path.txt") -> str:
    """
    Read the ``.canvas`` file path from a file.

    Reads only the first line, so multiple pathes can be stored in the file
    and swapped quickly by reordering lines — no need to delete or copy.

    :param path: Path to the file containing the canvas path
    :type path: ``str``
    :return: Path to the ``.canvas`` file
    :rtype: ``str``
    """
    with open(path) as f:
        return f.readline().strip()


# All special chars that must be escaped in MarkdownV2
_SPECIAL = r'_*[]()~`>#+-=|{}.!' 

def sanitize_markdown(text: str) -> str:
    result = []
    i = 0

    while i < len(text):
        # Already escaped sequence — pass through as-is
        if text[i] == '\\' and i + 1 < len(text) and text[i+1] in _SPECIAL:
            result.append(text[i:i+2])
            i += 2
            continue

        # Code block ```...```
        if text[i:i+3] == '```':
            end = text.find('```', i + 3)
            if end != -1:
                result.append(text[i:end+3])
                i = end + 3
                continue

        # Inline code `...`
        if text[i] == '`':
            end = text.find('`', i + 1)
            if end != -1:
                result.append(text[i:end+1])
                i = end + 1
                continue

        # Bold+italic ***...***
        if text[i:i+3] == '***':
            end = text.find('***', i + 3)
            if end != -1:
                result.append(text[i:end+3])
                i = end + 3
                continue

        # Bold **...** (standard md — should be gone after adapt_markdown)
        if text[i:i+2] == '**':
            end = text.find('**', i + 2)
            if end != -1:
                result.append(text[i:end+2])
                i = end + 2
                continue

        # Bold *...* (tg)
        if text[i] == '*':
            end = i + 1
            while end < len(text):
                if text[end] == '\\' and end + 1 < len(text) and text[end+1] in _SPECIAL:
                    end += 2
                    continue
                if text[end] == '*':
                    break
                end += 1
            if end < len(text):
                result.append(text[i:end+1])
                i = end + 1
                continue

        # Underline+italic ___...___
        if text[i:i+3] == '___':
            end = text.find('___', i + 3)
            if end != -1:
                result.append(text[i:end+3])
                i = end + 3
                continue

        # Underline __...__
        if text[i:i+2] == '__':
            end = text.find('__', i + 2)
            if end != -1:
                result.append(text[i:end+2])
                i = end + 2
                continue

        # Italic _..._
        if text[i] == '_':
            end = i + 1
            while end < len(text):
                if text[end] == '\\' and end + 1 < len(text) and text[end+1] in _SPECIAL:
                    end += 2
                    continue
                if text[end] == '_':
                    break
                end += 1
            if end < len(text):
                result.append(text[i:end+1])
                i = end + 1
                continue

        # Strikethrough ~~...~~
        if text[i:i+2] == '~~':
            end = text.find('~~', i + 2)
            if end != -1:
                result.append(text[i:end+2])
                i = end + 2
                continue

        # Strikethrough ~...~ (tg)
        if text[i] == '~':
            end = text.find('~', i + 1)
            if end != -1:
                result.append(text[i:end+1])
                i = end + 1
                continue

        # Spoiler ||...||
        if text[i:i+2] == '||':
            end = text.find('||', i + 2)
            if end != -1:
                result.append(text[i:end+2])
                i = end + 2
                continue

        # Link [text](url)
        if text[i] == '[':
            m = re.match(r'\[(.+?)\]\((.+?)\)', text[i:])
            if m:
                result.append(m.group(0))
                i += m.end()
                continue

        # Blockquote > (only at start of line)
        if text[i] == '>' and (i == 0 or text[i-1] == '\n'):
            end = text.find('\n', i)
            end = end if end != -1 else len(text)
            result.append(text[i:end])
            i = end
            continue

        # Plain special char — escape it
        if text[i] in _SPECIAL:
            result.append('\\' + text[i])
            i += 1
            continue

        result.append(text[i])
        i += 1

    return ''.join(result)

def adapt_markdown(text: str) -> str:
    """
    Adapt standard Markdown to Telegram-compatible Markdown.

    Telegram's Markdown mode uses ``*bold*`` and ``_italic_``,
    while most editors produce ``**bold**`` and ``*italic*``.

    Conversion rules:

    - ``**bold**``          → ``*bold*``
    - ``*italic*``          → ``_italic_``
    - ``***bold+italic***`` → ``*_bold+italic_*``
    - ``\\*escaped\\*``     → unchanged
    - Unclosed tags         → unchanged

    Supports nested and multiline strings.

    :param text: Markdown string to adapt
    :type text: ``str``
    :return: Telegram-compatible Markdown string
    :rtype: ``str``
    """

    result = []
    i = 0

    while i < len(text):
        # Skip escaped \*
        if text[i] == '\\' and i + 1 < len(text) and text[i+1] == '*':
            result.append(text[i:i+2])
            i += 2
            continue

        # Count consecutive *
        if text[i] == '*':
            stars = 0
            while i + stars < len(text) and text[i + stars] == '*':
                stars += 1

            # ***bold+italic***
            if stars >= 3:
                end = text.find('***', i + 3)
                if end != -1:
                    inner = adapt_markdown(text[i+3:end])
                    result.append(f'*_{inner}_*')
                    i = end + 3
                    continue

            # **bold**
            if stars >= 2:
                end = text.find('**', i + 2)
                if end != -1:
                    inner = adapt_markdown(text[i+2:end])
                    result.append(f'*{inner}*')
                    i = end + 2
                    continue

            # *italic*
            if stars >= 1:
                end = i + 1
                while end < len(text):
                    if text[end] == '\\' and end + 1 < len(text) and text[end+1] == '*':
                        end += 2
                        continue
                    if text[end] == '*' and (end + 1 >= len(text) or text[end+1] != '*'):
                        break
                    end += 1
                if end < len(text):
                    inner = adapt_markdown(text[i+1:end])
                    result.append(f'_{inner}_')
                    i = end + 1
                    continue

        result.append(text[i])
        i += 1

    return ''.join(result)

def telegramify_markdown(text: str):
    """
    Convert standard Markdown to a safe Telegram MarkdownV2 string.

    A convenience pipeline that combines :func:`adapt_markdown` and
    :func:`sanitize_markdown` in a single call:

    1. :func:`adapt_markdown` — converts ``**bold**`` → ``*bold*``,
       ``*italic*`` → ``_italic_``, ``***bold+italic***`` → ``*_..._*``
    2. :func:`sanitize_markdown` — escapes all special MarkdownV2
       characters outside of valid formatting entities

    :param text: Standard Markdown string
    :type text: ``str``
    :return: Safe MarkdownV2 string ready to send via Telegram Bot API
    :rtype: ``str``
    """
    return sanitize_markdown(
        adapt_markdown(text)
    )