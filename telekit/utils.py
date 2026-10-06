import os
import re
import difflib
import shlex

from pathlib import Path
from urllib.parse import urlencode, quote
from typing import Literal, Any, Iterable

from .html_text import HTMLText

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
# Environment: errors
# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

class EnvError(Exception):
    """Base class for all errors raised while reading env / token / canvas files."""


class EnvFileNotFoundError(EnvError, FileNotFoundError):
    """The file does not exist. The message contains commands to create it."""


class EnvPermissionError(EnvError, PermissionError):
    """The file cannot be read because of missing permissions."""


class EnvKeyError(EnvError, KeyError):
    """The requested variable is missing in the ``.env`` file."""

    def __str__(self) -> str:
        return str(self.args[0]) if self.args else ""


class EnvSyntaxError(EnvError, ValueError):
    """The ``.env`` file contains a line that cannot be parsed."""


class EnvValueError(EnvError, ValueError):
    """The file exists, but its content is empty, invalid or not UTF-8."""

# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# Environment: cache
# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

# Parsed ``.env`` files: absolute path -> {key: value}
_ENV_CACHE: dict[str, dict[str, str]] = {}
# Meaningful first line of plain text files (token.txt, canvas_path.txt): absolute path -> line
_TEXT_CACHE: dict[str, str] = {}


def clear_cache() -> None:
    """Drop everything cached by ``cache=True`` calls."""
    _ENV_CACHE.clear()
    _TEXT_CACHE.clear()


def _cache_key(path: str) -> str:
    return os.path.abspath(os.path.expanduser(path))

# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# Environment: error helpers
# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

def _create_commands(path: str, line: str) -> str:
    """Shell commands that append ``line`` to ``path`` (creating the file if needed)."""
    return "\n".join([
        f"    Linux/macOS:  printf '%s\\n' {shlex.quote(line)} >> {shlex.quote(path)}",
        f'    Win:          echo {line} >> "{path}"',
    ])


def _find_similar_files(path: str) -> list[str]:
    """Look for files with a similar name next to ``path`` and in the current directory."""
    p = Path(path)
    found: list[str] = []

    for folder in {p.parent, Path.cwd()}:
        try:
            if not folder.is_dir():
                continue
            names = [e.name for e in folder.iterdir() if e.is_file()]
        except OSError:
            continue

        close = set(difflib.get_close_matches(p.name, names, n=5, cutoff=0.6))
        if p.name.startswith(".env") or p.suffix == ".env":
            close |= {n for n in names if n.startswith(".env") or n.endswith(".env")}

        for name in sorted(close):
            candidate = str(folder / name)
            if _cache_key(candidate) != _cache_key(path) and candidate not in found:
                found.append(candidate)

    return found[:5]


def _missing_file_message(path: str, example: str, kind: str) -> str:
    p = Path(path)
    lines = [
        f"{kind} file not found: '{path}'",
        f"  Resolved to: {_cache_key(path)}",
        f"  Current working directory: {os.getcwd()}",
    ]

    if not p.parent.exists():
        lines += [
            f"  The directory '{p.parent}' does not exist either. Create it first:",
            f"    mkdir -p {shlex.quote(str(p.parent))}    (Windows: mkdir \"{p.parent}\")",
        ]

    similar = _find_similar_files(path)
    if similar:
        lines.append("  Similar files found - maybe you meant one of these:")
        lines += [f"    {s}" for s in similar]

    lines += [
        "  To create the file, run one of the commands below",
        f"  (replace the example value with your own):",
        _create_commands(path, example),
        "  Or pass the correct location, e.g. read_*(\"path/to/file\") "
        "(relative paths are resolved from the current working directory).",
    ]
    return "\n".join(lines)


def _syntax_error(source: str, lineno: int, line: str, problem: str, hint: str) -> EnvSyntaxError:
    return EnvSyntaxError(
        f"Invalid syntax in '{source}' at line {lineno}: {problem}\n"
        f"    > {line.strip()}\n"
        f"  Hint: {hint}"
    )


def _read_text(path: str, example: str, kind: str) -> str:
    """Read a text file as UTF-8 (BOM tolerated) and turn I/O errors into helpful ones."""
    try:
        return Path(path).read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        raise EnvFileNotFoundError(_missing_file_message(path, example, kind)) from None
    except IsADirectoryError:
        raise EnvError(
            f"Expected a file but '{path}' is a directory.\n"
            f"  Hint: pass the path to the file itself, e.g. '{os.path.join(path, '.env')}'."
        ) from None
    except PermissionError:
        raise EnvPermissionError(
            f"No permission to read '{path}'.\n"
            f"  Hint: check the access rights - Linux/macOS: `chmod u+r {shlex.quote(path)}`; "
            f"Windows: file Properties -> Security. Also make sure no other program locks the file."
        ) from None
    except UnicodeDecodeError as e:
        raise EnvValueError(
            f"'{path}' is not valid UTF-8 ({e.reason} at byte {e.start}).\n"
            f"  Hint: re-save the file in UTF-8 encoding (in most editors: "
            f"'Save with encoding' -> 'UTF-8')."
        ) from None
    except OSError as e:
        raise EnvError(
            f"Cannot read '{path}': {e.strerror or e}.\n"
            f"  Hint: check that the path is correct and the file is accessible."
        ) from None

# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# Environment: .env parser
# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

# Syntax supported:
#   # full-line comment
#   KEY=value                  unquoted, inline comment after " #"
#   export KEY=value           "export" prefix
#   KEY = value                spaces around "="
#   KEY=                       empty value
#   KEY='literal $value\n'     single quotes: no escapes, no interpolation
#   KEY="line1\nline2 \"q\""   double quotes: \n \r \t \" \\ \$ escapes + interpolation
#   KEY="multi                 quoted values may span several lines
#   line"
#   B=${A}/x  B=$A  B=${A:-d}  interpolation (earlier keys of the file, then os.environ);
#                              unknown variables without a default are left untouched
#   UTF-8 BOM and CRLF line endings are handled.

_KEY_RE = re.compile(r"^(?:export\s+)?([A-Za-z_][A-Za-z0-9_.\-]*)\s*=(.*)$")
_AFTER_QUOTE_RE = re.compile(r"^\s*(?:#.*)?$")
_INLINE_COMMENT_RE = re.compile(r"\s+#.*$")
_VAR_RE = re.compile(
    r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?:(:?-)([^}]*))?\}|\$([A-Za-z_][A-Za-z0-9_]*)"
)
_ESCAPES = {"n": "\n", "r": "\r", "t": "\t", '"': '"', "\\": "\\"}
_DOLLAR = "\x00"  # placeholder for an escaped "\$" until interpolation is done


def _scan_double_quoted(s: str) -> tuple[str, int] | None:
    """Scan ``s`` (text after an opening ``"``). Return (value, index of closing quote) or None."""
    out: list[str] = []
    i = 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s):
            nxt = s[i + 1]
            if nxt in _ESCAPES:
                out.append(_ESCAPES[nxt])
            elif nxt == "$":
                out.append(_DOLLAR)
            else:
                out.append("\\" + nxt)  # unknown escape stays as is
            i += 2
            continue
        if c == '"':
            return "".join(out), i
        out.append(c)
        i += 1
    return None


def _interpolate(value: str, env: dict[str, str]) -> str:
    def repl(m: re.Match) -> str:
        name = m.group(1) or m.group(4)
        op, default = m.group(2), m.group(3)
        found = env.get(name, os.environ.get(name))

        if op == ":-" and not found:
            return default or ""
        if op == "-" and found is None:
            return default or ""
        return m.group(0) if found is None else found

    return _VAR_RE.sub(repl, value).replace(_DOLLAR, "$")


def _parse_env(text: str, source: str) -> dict[str, str]:
    """Parse the content of a ``.env`` file. ``source`` is only used in error messages."""
    env: dict[str, str] = {}
    lines = text.lstrip("\ufeff").splitlines()
    i = 0

    while i < len(lines):
        raw = lines[i]
        lineno = i + 1
        stripped = raw.strip()

        if not stripped or stripped.startswith("#"):
            i += 1
            continue

        m = _KEY_RE.match(stripped)
        if not m:
            if "=" not in stripped:
                raise _syntax_error(
                    source, lineno, raw, "missing '='",
                    f"write the line as KEY=value, or start it with '#' to make it a comment, "
                    f"e.g. '{stripped.split()[0]}=your_value'.",
                )
            raise _syntax_error(
                source, lineno, raw, "invalid variable name",
                "names may contain letters, digits, '_', '.', '-' and must not start with a digit "
                "or contain spaces, e.g. MY_TOKEN=value.",
            )

        key, rest = m.group(1), m.group(2).strip()

        if rest[:1] in ('"', "'"):
            quote_char = rest[0]
            body = rest[1:]
            start_line = lineno

            while True:
                if quote_char == '"':
                    scanned = _scan_double_quoted(body)
                else:
                    end = body.find("'")
                    scanned = (body[:end], end) if end != -1 else None

                if scanned is not None:
                    break
                i += 1
                if i >= len(lines):
                    raise _syntax_error(
                        source, start_line, raw, f"unclosed {quote_char} quote",
                        f"add the closing {quote_char} at the end of the value. For text that "
                        f"contains the same quote, use the other quote type"
                        + (' or escape it as \\"' if quote_char == '"' else "") + ".",
                    )
                body += "\n" + lines[i]

            value, end = scanned
            tail = body[end + 1:]
            if not _AFTER_QUOTE_RE.match(tail):
                raise _syntax_error(
                    source, start_line, raw, f"unexpected text after closing quote: {tail.strip()!r}",
                    "put comments after whitespace and '#', or quote the whole value "
                    "(escape inner double quotes as \\\").",
                )

            if quote_char == '"':
                value = _interpolate(value, env)
        else:
            if rest.startswith("#"):
                rest = ""
            value = _interpolate(_INLINE_COMMENT_RE.sub("", rest).strip(), env)

        env[key] = value
        i += 1

    return env


def _split_env_path(path: str, default: str) -> tuple[str, str]:
    """Split ``"file.env:KEY"`` into ``("file.env", "KEY")``. Windows drive letters are safe."""
    m = re.match(r"^(.+):([A-Za-z_][A-Za-z0-9_.\-]*)$", path)
    if m:
        return m.group(1), m.group(2)
    return path, default


def _is_env_path(path: str) -> bool:
    base = os.path.basename(_split_env_path(path, "")[0])
    return base.endswith(".env") or base.startswith(".env")


def _load_env(path: str, cache: bool, example: str) -> dict[str, str]:
    key = _cache_key(path)

    if not (cache and key in _ENV_CACHE):
        text = _read_text(path, example, ".env")
        _ENV_CACHE[key] = _parse_env(text, path)

    return dict(_ENV_CACHE[key])


def load_env(path=".env", *, cache: bool = True) -> dict[str, str]:
    """
    Load all key-value pairs from a ``.env`` file.

    Supported syntax: ``KEY=value``, ``export KEY=value``, spaces around ``=``,
    full-line and inline (`` # ...``) comments, empty values, single-quoted
    (literal) and double-quoted values with ``\\n \\r \\t \\" \\\\ \\$`` escapes,
    multi-line quoted values, ``$VAR`` / ``${VAR}`` / ``${VAR:-default}``
    interpolation, UTF-8 BOM and CRLF line endings.

    :param path: Path to the ``.env`` file. Defaults to ``".env"``.
    :type path: ``str``
    :param cache: If ``True`` (default) and the file was already parsed, return
        the in-memory result without touching the disk. If ``False``, the file
        is always read and parsed again, and the cache is updated.
    :type cache: ``bool``
    :return: Dictionary of all key-value pairs found in the file.
    :rtype: ``dict[str, str]``
    :raises EnvFileNotFoundError: If the file does not exist (the message
        contains shell commands to create it). Subclass of ``FileNotFoundError``.
    :raises EnvSyntaxError: If a line cannot be parsed (the message contains
        the line number and a hint). Subclass of ``ValueError``.
    :raises EnvPermissionError: If the file cannot be read.
    :raises EnvValueError: If the file is not UTF-8.
    """
    return _load_env(path, cache, "KEY=value")


def read_envar(path: str, name: str, *, cache: bool = True) -> str:
    """
    Read a single environment variable from a ``.env`` file.

    :param path: Path to the ``.env`` file.
    :type path: ``str``
    :param name: Name of the key to read.
    :type name: ``str``
    :param cache: Use the in-memory copy of the file if available
        (see :func:`load_env`). Default is ``True``.
    :type cache: ``bool``
    :return: Value of the key (may be an empty string if it is declared empty).
    :rtype: ``str``
    :raises EnvKeyError: If ``name`` is not found in the file. The message
        lists available keys, close matches and the command to add the key.
        Subclass of ``KeyError``.
    :raises EnvFileNotFoundError: See :func:`load_env`.
    """
    example = f"{name}=your_value"
    env = _load_env(path, cache, example)

    if name in env:
        return env[name]

    lines = [f"Variable '{name}' not found in '{path}'."]

    lower = {k.lower(): k for k in env}
    if name.lower() in lower:
        lines.append(
            f"  Names are case-sensitive: the file has '{lower[name.lower()]}', not '{name}'."
        )

    close = difflib.get_close_matches(name, list(env), n=3, cutoff=0.6)
    close = [c for c in close if c != lower.get(name.lower())]
    if close:
        lines.append("  Did you mean: " + ", ".join(f"'{c}'" for c in close) + "?")

    if env:
        lines.append("  Variables in this file: " + ", ".join(env))
    else:
        lines.append("  The file contains no variables (it is empty or has only comments).")

    lines += [
        f"  To fix it, add the line `{example}` to '{path}':",
        _create_commands(path, example),
        "  Check also that the line is not commented out with '#' "
        "and that you are reading the right file.",
    ]
    if cache:
        lines.append("  If you edited the file after the first read, call again with cache=False (or clear_cache()).")

    raise EnvKeyError("\n".join(lines))


def _read_first_value(path: str, example: str, kind: str, cache: bool) -> str:
    """First meaningful (non-empty, non-comment) line of a plain text file."""
    key = _cache_key(path)
    if cache and key in _TEXT_CACHE:
        return _TEXT_CACHE[key]

    text = _read_text(path, example, kind)

    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            _TEXT_CACHE[key] = line
            return line

    _TEXT_CACHE.pop(key, None)
    raise EnvValueError(
        f"{kind} file '{path}' is empty (no lines other than blanks and '#' comments).\n"
        f"  Write the value on the first line, e.g. `{example}`:\n"
        f"{_create_commands(path, example)}"
    )


def read_token(path: str = "token.txt", *, cache: bool = True) -> str:
    """
    Read the bot token from a file or ``.env``.

    **Plain text file** (default)::

        # token.txt
        123456789:BotSecretToken  Main production bot
        987654321:AnotherToken    Backup bot

    Reads only the first meaningful line (blank lines and ``#`` comments are
    skipped). Inline comments (everything after the first whitespace) are
    ignored. Multiple tokens can be stored and swapped by reordering lines.

    **Environment file** (``.env``)::

        read_token(".env")          # reads the key named TOKEN
        read_token(".env:TOKEN")    # same, explicit key
        read_token(".env:BOT_KEY")  # reads a custom key

    :param path: Path to a token file, or ``".env"`` / ``".env:KEY"`` for
                 environment files. Defaults to ``"token.txt"``.
    :type path: ``str``
    :param cache: If ``True`` (default), use the in-memory copy if available; if
                  ``False``, re-read the file and refresh the cache.
    :type cache: ``bool``
    :return: Bot token string.
    :rtype: ``str``
    :raises EnvKeyError: If the key is not found in the ``.env`` file.
    :raises EnvFileNotFoundError: If the file does not exist (message contains
        commands to create it).
    :raises EnvValueError: If the file or the value is empty.
    """
    example = "123456789:YourBotToken"

    if _is_env_path(path):
        file_path, name = _split_env_path(path, "TOKEN")
        token = read_envar(file_path, name, cache=cache).strip()

        if not token:
            raise EnvValueError(
                f"Variable '{name}' in '{file_path}' is empty.\n"
                f"  Hint: set the token after '=', e.g. `{name}={example}` "
                f"(get one from @BotFather in Telegram)."
            )
        return token

    line = _read_first_value(path, example, "Token", cache)
    return line.split()[0]


def read_canvas_path(path: str = "canvas_path.txt", *, cache: bool = True) -> str:
    """
    Read the ``.canvas`` file path from a file or ``.env``.

    **Plain text file** (default)::

        # canvas_path.txt
        /home/user/project/main.canvas  Production canvas
        /home/user/project/test.canvas  Test canvas

    Reads only the first meaningful line (blank lines and ``#`` comments are
    skipped). A comment may follow the path after two or more spaces or a tab
    (single spaces are part of the path). Multiple paths can be stored and
    swapped by reordering lines.

    **Environment file** (``.env``)::

        read_canvas_path(".env")               # reads the key named CANVAS_PATH
        read_canvas_path(".env:CANVAS_PATH")   # same, explicit key
        read_canvas_path(".env:MY_CANVAS")     # reads a custom key

    :param path: Path to a canvas path file, or ``".env"`` / ``".env:KEY"`` for
                 environment files. Defaults to ``"canvas_path.txt"``.
    :type path: ``str``
    :param cache: If ``True`` (default), use the in-memory copy if available; if
                  ``False``, re-read the file and refresh the cache.
    :type cache: ``bool``
    :return: Path to the ``.canvas`` file.
    :rtype: ``str``
    :raises EnvKeyError: If the key is not found in the ``.env`` file.
    :raises EnvFileNotFoundError: If the file does not exist (message contains
        commands to create it).
    :raises EnvValueError: If the file or the value is empty.
    """
    example = "/path/to/project/main.canvas"

    if _is_env_path(path):
        file_path, name = _split_env_path(path, "CANVAS_PATH")
        value = read_envar(file_path, name, cache=cache).strip()

        if not value:
            raise EnvValueError(
                f"Variable '{name}' in '{file_path}' is empty.\n"
                f"  Hint: set the path after '=', e.g. `{name}={example}`."
            )
        return value

    line = _read_first_value(path, example, "Canvas path", cache)
    return re.split(r"\s{2,}|\t", line, maxsplit=1)[0]
    
# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# Inline Keyboards
# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

def compose_keyboard(
    *groups: dict[str, Any],
    widths: Iterable[int] = (1, -1),
) -> tuple[dict[str, Any], tuple[int, ...]]:
    """
    Merge multiple button groups into a single keyboard dict with computed row widths.

    Each group is laid out independently using its corresponding width from ``widths``.
    A width of ``-1`` means "all buttons in one row" (i.e. ``len(group)``).

    :param groups: One or more dicts mapping button labels to values.
    :type groups: ``dict[str, Any]``
    :param widths: Row width for each group. Must match the number of groups,
                   or be a single value applied to all groups.
                   Use ``-1`` to fit the entire group on one row.
    :type widths: ``Iterable[int]``
    :return: Merged keyboard dict and the computed row_width tuple.
    :rtype: ``tuple[dict[str, Any], tuple[int, ...]]``

    Example::

        keyboard, row_width = compose_keyboard(
            {"🆕 Create": "create"},
            {str(n): str(n) for n in range(1, 10)},
            {"« Back": "back", "Next »": "next"},
            widths=(1, 3, -1),
        )
        chain.set_inline_choice(keyboard, row_width)
        # row_width → (1, 3, 3, 3, 2)
        # layout:
        #   | 🆕 Create        |
        #   | 1  | 2  | 3      |
        #   | 4  | 5  | 6      |
        #   | 7  | 8  | 9      |
        #   | « Back | Next »  |
    """
    widths_list = list(widths)

    if len(widths_list) == 1:
        widths_list = widths_list * len(groups)

    if len(widths_list) != len(groups):
        raise ValueError(
            f"Number of widths ({len(widths_list)}) must match "
            f"number of groups ({len(groups)}) or be 1."
        )

    keyboard: dict[str, Any] = {}
    row_width: list[int] = []

    for group, width in zip(groups, widths_list):
        if not group:
            continue

        count = len(group)
        w = count if width == -1 else width

        full_rows = count // w
        remainder = count % w

        row_width.extend([w] * full_rows)
        if remainder:
            row_width.append(remainder)

        keyboard.update(group)

    return keyboard, tuple(row_width)


# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# Link Generating
# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

def make_mention(user_id: int | str) -> str:
    """
    Creates a Telegram mention link by user ID.

    Examples::

        make_mention(123456789)
        >>> 'tg://user?id=123456789'
    """
    return f"tg://user?id={user_id}"

def make_bot_link(botname: str, start: str | None = None, escape: bool = True) -> str:
    """
    Return a t.me link to a bot.

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
    encoded_start = quote(start, safe="") if escape else start
    return f"https://t.me/{botname}?start={encoded_start}"

def make_user_link(username: str, text: str | None = None, escape: bool = True) -> str:
    """
    Return a t.me link to a user.

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
    encoded_text = quote(text, safe="") if escape else text
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
    """
    Return a QuickChart URL that renders a QR code.

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
        params["dark"] = dark.lstrip("#")
    if light is not None: 
        params["light"] = light.lstrip("#")
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
# Tools
# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

import importlib
import pkgutil

def load_modules(package_name: str) -> None:
    """
    Automatically import all modules inside the given package.

    Finds every submodule of ``package_name`` (skipping ones that start
    with ``_``) and imports each one, so their top-level code (e.g.
    handler class definitions) runs and gets registered.

    .. warning::
        Modules are imported in filename order (usually alphabetical). 
        If handlers have overlapping triggers,
        the one imported first may shadow the others.

        Fix: manually import the priority modules first, then call
        ``load_modules`` -- Python skips modules that are already
        imported, so they won't be re-imported or reordered::

            from . import on_text  # will be checked before other handlers

            telekit.utils.load_modules(__name__)

    :param package_name: Dotted name of the package to load
        (typically ``__name__``).
    :type package_name: str

    :Example:

    .. code-block:: python

        # handlers/__init__.py
        import telekit
        telekit.utils.load_modules(__name__)
    """
    package = importlib.import_module(package_name)

    for module in pkgutil.iter_modules(package.__path__):
        if module.name.startswith("_"):
            continue

        importlib.import_module(f"{package_name}.{module.name}")

class CyclicList:
    def __init__(self, *items):
        self._items = list(items)

    def __getitem__(self, index: int):
        return self._items[index % len(self._items)]

    def __len__(self):
        return len(self._items) # Actually `float("inf")` ;)

    def __repr__(self):
        return f"CyclicList({self._items})"

    
# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# Markdown Sanitizing
# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

import re


class TelegramMarkdownV2Sanitizer:
    """
    Soft parser/sanitizer for Telegram MarkdownV2.

    Idea: scan the text left to right, recognize valid (i.e. correctly
    CLOSED) markup tags (*bold*, _italic_, __underline__,
    ~strike~, ||spoiler||, `code`, ```pre```, [text](url), >quote),
    recursively sanitize their content and leave the markup unescaped.

    If a matching closing token is not found, the character is
    treated as plain text and escaped.
    """

    # Characters that MarkdownV2 requires to be escaped in plain text
    ESCAPE_SPECIAL = r'_*[]()~`>#+-=|{}.!'

    def sanitize(self, text: str) -> str:
        return self._parse(text)

    # ---------- helper methods ----------

    def _escape_literal(self, ch: str) -> str:
        if ch == '\\':
            return '\\\\'
        if ch in self.ESCAPE_SPECIAL:
            return '\\' + ch
        return ch

    def _escape_plain_run(self, s: str) -> str:
        return ''.join(self._escape_literal(c) for c in s)

    def _escape_code(self, s: str) -> str:
        # Inside code/pre only backslash and backtick need escaping
        return s.replace('\\', '\\\\').replace('`', '\\`')

    def _find_closing(self, s: str, start: int, token: str) -> int:
        """
        Finds the nearest UNescaped occurrence of token, skipping
        escape sequences and inline/block code spans (their content
        is considered "foreign territory" and cannot close an outer tag).
        """
        i = start
        n = len(s)
        tlen = len(token)
        while i < n:
            c = s[i]
            if c == '\\' and i + 1 < n:
                i += 2
                continue
            if s[i:i + 3] == '```':
                end = s.find('```', i + 3)
                i = end + 3 if end != -1 else n
                continue
            if c == '`':
                end = s.find('`', i + 1)
                i = end + 1 if end != -1 else n
                continue
            if s[i:i + tlen] == token:
                return i
            i += 1
        return -1

    # ---------- main parser ----------

    def _parse(self, s: str) -> str:
        out = []
        i = 0
        n = len(s)

        while i < n:
            c = s[i]

            # 1. Already escaped character - leave as is
            if c == '\\':
                if i + 1 < n and (s[i + 1] in self.ESCAPE_SPECIAL or s[i + 1] == '\\'):
                    out.append('\\' + s[i + 1])
                    i += 2
                else:
                    # "bare" backslash at the end of the string or before a non-special char
                    out.append('\\\\')
                    i += 1
                continue

            # 2. Code block ```...```
            if s[i:i + 3] == '```':
                end = s.find('```', i + 3)
                if end != -1 and end > i + 3:
                    inner = s[i + 3:end]
                    out.append('```' + self._escape_code(inner) + '```')
                    i = end + 3
                    continue
                out.append(self._escape_literal(c))
                i += 1
                continue

            # 3. Inline code `...`
            if c == '`':
                end = s.find('`', i + 1)
                if end != -1 and end > i + 1:
                    inner = s[i + 1:end]
                    out.append('`' + self._escape_code(inner) + '`')
                    i = end + 1
                    continue
                out.append(self._escape_literal(c))
                i += 1
                continue

            # 4. Link [text](url)
            if c == '[':
                m = re.match(r'\[((?:[^\[\]\\]|\\.)*)\]\(((?:[^()\\]|\\.)*)\)', s[i:])
                if m:
                    inner_text = self._parse(m.group(1))
                    url = m.group(2).replace('\\', '\\\\').replace(')', '\\)')
                    out.append('[' + inner_text + '](' + url + ')')
                    i += m.end()
                    continue
                out.append(self._escape_literal(c))
                i += 1
                continue

            # 5. Spoiler ||...||
            if s[i:i + 2] == '||':
                close = self._find_closing(s, i + 2, '||')
                if close != -1 and close > i + 2:
                    out.append('||' + self._parse(s[i + 2:close]) + '||')
                    i = close + 2
                    continue
                out.append(self._escape_literal('|'))
                i += 1
                continue

            # 6. Underline __...__
            if s[i:i + 2] == '__':
                close = self._find_closing(s, i + 2, '__')
                if close != -1 and close > i + 2:
                    out.append('__' + self._parse(s[i + 2:close]) + '__')
                    i = close + 2
                    continue
                out.append(self._escape_literal('_'))
                i += 1
                continue

            # 7. Legacy **bold** (from markdown, if not adapted) -> single *
            if s[i:i + 2] == '**':
                close = self._find_closing(s, i + 2, '**')
                if close != -1 and close > i + 2:
                    out.append('*' + self._parse(s[i + 2:close]) + '*')
                    i = close + 2
                    continue
                out.append(self._escape_literal('*'))
                i += 1
                continue

            # 8. Bold *...*
            if c == '*':
                close = self._find_closing(s, i + 1, '*')
                if close != -1 and close > i + 1:
                    out.append('*' + self._parse(s[i + 1:close]) + '*')
                    i = close + 1
                    continue
                out.append(self._escape_literal(c))
                i += 1
                continue

            # 9. Italic _..._
            if c == '_':
                close = self._find_closing(s, i + 1, '_')
                if close != -1 and close > i + 1:
                    out.append('_' + self._parse(s[i + 1:close]) + '_')
                    i = close + 1
                    continue
                out.append(self._escape_literal(c))
                i += 1
                continue

            # 10. Strikethrough ~...~
            if c == '~':
                close = self._find_closing(s, i + 1, '~')
                if close != -1 and close > i + 1:
                    out.append('~' + self._parse(s[i + 1:close]) + '~')
                    i = close + 1
                    continue
                out.append(self._escape_literal(c))
                i += 1
                continue

            # 11. Quote > (only at the start of a line)
            if c == '>' and (i == 0 or s[i - 1] == '\n'):
                end = s.find('\n', i)
                end = end if end != -1 else n
                out.append('>' + self._parse(s[i + 1:end]))
                i = end
                continue

            # 12. Regular character
            out.append(self._escape_literal(c))
            i += 1

        return ''.join(out)


def sanitize_markdown(text: str) -> str:
    """Backward-compatible wrapper function."""
    return TelegramMarkdownV2Sanitizer().sanitize(text)

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