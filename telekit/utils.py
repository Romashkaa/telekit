import os
import re

from pathlib import Path
from urllib.parse import urlencode, quote
from typing import Literal

ROOT_DIR = Path(__file__).resolve().parent  # telekit/

# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# Checks
# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

def is_valid_callback_data(callback_data: str) -> bool:
    """
    Check whether a callback data string is valid for Telegram inline buttons.

    Telegram requires callback data to be between 1 and 64 bytes (UTF-8 encoded).

    :param callback_data: Callback data string to validate.
    :type callback_data: `str`
    :return: `True` if the string is within the allowed byte range, `False` otherwise.
    :rtype: `bool`

    Examples:

        >>> is_valid_callback_data("buy")
        True

        >>> is_valid_callback_data("")
        False

        >>> is_valid_callback_data("a" * 65)
        False
    """
    byte_size = len(callback_data.encode('utf-8'))
    return 1 <= byte_size <= 64

# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# Formatting
# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

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

# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# Environment
# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

def _split_env_path(path: str, default: str) -> tuple[str, str]:
    if ":" in path:
        path, name = path.split(":", 1)
    else:
        path, name = path, default

    return path, name


def load_env(path=".env") -> dict[str, str]:
    """
    Load all key-value pairs from a ``.env`` file.

    Lines starting with ``#`` and empty lines are ignored.

    :param path: Path to the ``.env`` file. Defaults to ``".env"``.
    :type path: ``str``
    :return: Dictionary of all key-value pairs found in the file,
             or an empty dict if the file does not exist.
    :rtype: ``dict[str, str]``
    """
    if not os.path.exists(path):
        return {}
    
    env: dict[str, str] = {}
        
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            key, value = line.split("=", 1)
            env[key.strip()] = value.strip()

    return env


def read_envar(path: str, name: str) -> str:
    """
    Read a single environment variable from a ``.env`` file.

    :param path: Path to the ``.env`` file.
    :type path: ``str``
    :param name: Name of the key to read.
    :type name: ``str``
    :return: Value of the key.
    :rtype: ``str``
    :raises KeyError: If ``name`` is not found in the file.
    """
    env: dict[str, str] = load_env(path)

    if name not in env:
        raise KeyError(f"{name} not found in {path}")

    return env[name]


def read_token(path: str = "token.txt") -> str:
    """
    Read the bot token from a file or ``.env``.

    **Plain text file** (default)::

        # token.txt
        123456789:BotSecretToken  Main production bot
        987654321:AnotherToken    Backup bot

    Reads only the first line. Inline comments (everything after the first
    whitespace) are ignored. Multiple tokens can be stored and swapped by
    reordering lines.

    **Environment file** (``.env``)::

        read_token(".env")          # reads the key named TOKEN
        read_token(".env:TOKEN")    # same, explicit key
        read_token(".env:BOT_KEY")  # reads a custom key

    :param path: Path to a token file, or ``".env"`` / ``".env:KEY"`` for
                 environment files. Defaults to ``"token.txt"``.
    :type path: ``str``
    :return: Bot token string.
    :rtype: ``str``
    :raises KeyError: If the key is not found in the ``.env`` file.
    :raises FileNotFoundError: If the file does not exist.
    """
    if path.endswith(".env") or ".env:" in path:
        return read_envar(*_split_env_path(path, "TOKEN"))
    
    with open(path) as f:
        first_line: str = f.readline().strip()
        token, *_ = first_line.split()
        return token
    

def read_canvas_path(path: str = "canvas_path.txt") -> str:
    """
    Read the ``.canvas`` file path from a file or ``.env``.

    **Plain text file** (default)::

        # canvas_path.txt
        /home/user/project/main.canvas  Production canvas
        /home/user/project/test.canvas  Test canvas

    Reads only the first line. Multiple paths can be stored and swapped by
    reordering lines.

    **Environment file** (``.env``)::

        read_canvas_path(".env")               # reads the key named CANVAS_PATH
        read_canvas_path(".env:CANVAS_PATH")   # same, explicit key
        read_canvas_path(".env:MY_CANVAS")     # reads a custom key

    :param path: Path to a canvas path file, or ``".env"`` / ``".env:KEY"`` for
                 environment files. Defaults to ``"canvas_path.txt"``.
    :type path: ``str``
    :return: Path to the ``.canvas`` file.
    :rtype: ``str``
    :raises KeyError: If the key is not found in the ``.env`` file.
    :raises FileNotFoundError: If the file does not exist.
    """
    if path.endswith(".env") or ".env:" in path:
        return read_envar(*_split_env_path(path, "CANVAS_PATH"))
    
    with open(path) as f:
        return f.readline().strip()
    
# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# Link Generating
# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

def make_bot_link(botname: str, start: str | None = None) -> str:
    """Return a t.me link to a bot.

    >>> make_bot_link("UserNameOfBot")
    "https://t.me/UserNameOfBot"

    >>> make_bot_link("UserNameOfBot", start="Hello!")
    "https://t.me/UserNameOfBot?start=Hello%21"

    Args:
        botname: Bot username with or without leading '@'.
        start:   Optional deep-link payload appended as ?start=.

    Returns:
        A t.me URL string.
    """
    botname = botname.lstrip("@")
    if start is None:
        return f"https://t.me/{botname}"
    encoded_start = quote(start, safe="")
    return f"https://t.me/{botname}?start={encoded_start}"

def make_user_link(username: str, text: str | None = None) -> str:
    """Return a t.me link to a user.

    >>> make_user_link("UserName")
    "https://t.me/UserName"

    >>> make_user_link("UserName", text="Hello!")
    "https://t.me/UserName?text=Hello%21"

    Args:
        username: Telegram username with or without leading '@'.
        text:     Optional pre-filled message text appended as ?text=.

    Returns:
        A t.me URL string.
    """
    username = username.lstrip("@")
    if text is None:
        return f"https://t.me/{username}"
    encoded_text = quote(text, safe="")
    return f"https://t.me/{username}?text={encoded_text}"

def make_qrcode(
    text: str,
    *,
    size: int | None = None,
    margin: int | None = None,
    dark: str | None = None,
    light: str | None = None,
    ec_level: Literal["L", "M", "Q", "H"] | None = None,
    format: Literal["png", "svg", "base64"] | None = None,
    center_image_url: str | None = None,
    center_image_size_ratio: float | None = None,
    center_image_width: int | None = None,
    center_image_height: int | None = None,
    caption: str | None = None,
    caption_font_family: str | None = None,
    caption_font_size: int | None = None,
    caption_font_color: str | None = None,
) -> str:
    """Return a QuickChart URL that renders a QR code.

    >>> make_qrcode("https://example.com")
    'https://quickchart.io/qr?text=https%3A%2F%2Fexample.com'

    >>> make_qrcode("Hello", dark="ff0000", size=300)
    'https://quickchart.io/qr?text=Hello&size=300&dark=ff0000'

    Use with sender:
    >>> sender.set_photo(make_qrcode("https://example.com", caption="Scan Me"))

    Check out the [QuickChart QR Code API](https://quickchart.io/documentation/qr-codes/)

    Args:
        text:                   Content to encode (URL or any string).
        size:                   Width and height of the image in pixels.
        margin:                 Whitespace around the QR image in modules.
        dark:                   Hex color of dark cells, without '#'.
        light:                  Hex color of light cells, without '#'.
                                Use "0000" for a transparent background.
        ec_level:               Error correction level — L, M, Q, or H.
        format:                 Output format — png, svg, or base64.
        center_image_url:       URL of an image to display in the center.
                                Must be publicly accessible (PNG or JPG).
        center_image_size_ratio: Float 0.0–1.0 — portion of QR area the
                                center image occupies. Keep below ~0.3.
        center_image_width:     Center image width in pixels.
        center_image_height:    Center image height in pixels.
        caption:                Caption text displayed below the QR code.
        caption_font_family:    Font family of the caption.
        caption_font_size:      Font size of the caption in pixels.
        caption_font_color:     Color of the caption — name or hex.

    Returns:
        A quickchart.io URL string.
    """
    params: dict = {"text": text}

    if size is not None: 
        params["size"] = size
    if margin is not None: 
        params["margin"] = margin
    if dark is not None: 
        params["dark"] = dark
    if light is not None: 
        params["light"] = light
    if ec_level is not None: 
        params["ecLevel"] = ec_level
    if format is not None: 
        params["format"] = format
    if center_image_url is not None: 
        params["centerImageUrl"] = center_image_url
    if center_image_size_ratio is not None: 
        params["centerImageSizeRatio"] = center_image_size_ratio
    if center_image_width is not None: 
        params["centerImageWidth"] = center_image_width
    if center_image_height is not None: 
        params["centerImageHeight"] = center_image_height
    if caption is not None: 
        params["caption"] = caption
    if caption_font_family is not None: 
        params["captionFontFamily"] = caption_font_family
    if caption_font_size is not None: 
        params["captionFontSize"] = caption_font_size
    if caption_font_color is not None: 
        params["captionFontColor"] = caption_font_color

    return "https://quickchart.io/qr?" + urlencode(params, quote_via=quote)

# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# Markdown Sanitizing
# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

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