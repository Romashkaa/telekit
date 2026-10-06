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

import html as _html
import json
import re
from html.parser import HTMLParser


## PATCH

from telebot import types

_orig_de_json = types.RichText.de_json

def _safe_rich_text_de_json(obj):
    if isinstance(obj, list):
        return [_safe_rich_text_de_json(item) for item in obj]
    try:
        return _orig_de_json(obj)
    except TypeError:
        return obj  # leave the raw value instead of crashing the whole update

types.RichText.de_json = staticmethod(_safe_rich_text_de_json)

## PATCH

__all__ = [
    "RichMessageError", "RICH_MAX_LENGTH", "RICH_ONLY_TAGS",
    "find_rich_tags", "find_invalid_media_sources",
    "downgrade_rich_html", "build_media_html", "serialize_rich_message",
    "newlines_to_br",
]

RICH_MAX_LENGTH = 32_768


class RichMessageError(ValueError):
    """Raised when a rich message cannot be built or sent."""


# Tags that exist ONLY in Rich HTML (regular parse_mode="html" rejects them)
RICH_ONLY_TAGS = frozenset({
    "h1", "h2", "h3", "h4", "h5", "h6", "p", "br", "footer", "hr",
    "ul", "ol", "li", "mark", "sub", "sup",
    "img", "video", "audio", "figure", "figcaption", "cite", "aside",
    "details", "summary", "table", "caption", "tr", "td", "th",
    "tg-map", "tg-collage", "tg-slideshow",
    "tg-math", "tg-math-block", "tg-reference", "tg-time", "tg-thinking",
})

_TAG_RE = re.compile(r"<\s*/?\s*([A-Za-z][\w-]*)([^<>]*)>")
_ANCHOR_ATTR_RE = re.compile(r"""\bname\s*=|\bhref\s*=\s*["']?#""", re.I)
_MEDIA_SRC_RE = re.compile(
    r"""<\s*(?:img|video|audio)\b[^<>]*?\bsrc\s*=\s*(["'])(.*?)\1""", re.I | re.S
)


def find_rich_tags(text: str) -> list[str]:
    """Returns names of rich-only tags found in the HTML text (unique, in order)."""
    found: list[str] = []
    for match in _TAG_RE.finditer(text):
        name = match.group(1).lower()
        if name == "a" and _ANCHOR_ATTR_RE.search(match.group(2)):
            name = "a (anchor)"
        elif name not in RICH_ONLY_TAGS:
            continue
        if name not in found:
            found.append(name)
    return found


def find_invalid_media_sources(text: str) -> list[str]:
    """Media `src` values that are neither http(s):// nor tg://."""
    result = []
    for match in _MEDIA_SRC_RE.finditer(text):
        src = _html.unescape(match.group(2)).strip()
        if not src.lower().startswith(("http://", "https://", "tg://")):
            result.append(src)
    return result


def build_media_html(urls: list[str]) -> str:
    if not urls:
        return ""
    images = [f'<img src="{_html.escape(url, quote=True)}"/>' for url in urls]
    if len(images) == 1:
        return images[0]
    return "<tg-collage>" + "".join(images) + "</tg-collage>"


def serialize_rich_message(
    html_text: str, *, is_rtl: bool | None = None, skip_entity_detection: bool | None = None
) -> str:
    data: dict = {"html": html_text}
    if is_rtl is not None:
        data["is_rtl"] = is_rtl
    if skip_entity_detection is not None:
        data["skip_entity_detection"] = skip_entity_detection
    return json.dumps(data, ensure_ascii=False)


# ---------------------------------------------------------------------------
# "\n" -> <br/> for Rich HTML
# ---------------------------------------------------------------------------

_BR = "<br/>"
_SPLIT_RE = re.compile(r"(<[^<>]*>)")

# newlines inside these are kept as is
_RAW_TAGS = frozenset({"pre", "code", "tg-math", "tg-math-block"})

# block-level tags: a newline right next to them is just whitespace
_BLOCK_TAGS = frozenset({
    "h1", "h2", "h3", "h4", "h5", "h6", "p", "footer", "hr", "br",
    "ul", "ol", "li", "figure", "figcaption", "aside", "details", "summary",
    "table", "caption", "tr", "td", "th", "blockquote", "pre",
    "img", "video", "audio", "tg-map", "tg-collage", "tg-slideshow", "tg-math-block",
})


def _tag_info(token: str):
    """Returns (name, is_closing, is_self_closing) for a tag token, or None."""
    match = _TAG_RE.fullmatch(token)
    if not match:
        return None
    closing = token[1:].lstrip().startswith("/")
    self_closing = token[:-1].rstrip().endswith("/")
    return match.group(1).lower(), closing, self_closing


def newlines_to_br(text: str) -> str:
    """
    Converts "\\n" in Rich HTML text to ``<br/>``.

    - newlines inside ``<pre>``, ``<code>`` and ``<tg-math*>`` are preserved;
    - newlines adjacent to block tags (``<h1>``, ``<p>``, ``<ul>``, ``<blockquote>``...)
      and at the very start/end of the text are dropped, because blocks already
      separate themselves (otherwise ``Stack``/``Quote``/``Language``, which add
      their own "\\n", would produce empty lines).
    """
    parts = _SPLIT_RE.split(text.replace("\r\n", "\n"))
    infos = [_tag_info(p) if i % 2 else None for i, p in enumerate(parts)]

    out: list[str] = []
    raw_depth = 0

    for i, part in enumerate(parts):
        if i % 2:  # tag
            info = infos[i]
            if info and info[0] in _RAW_TAGS:
                _, closing, self_closing = info
                if closing:
                    raw_depth = max(0, raw_depth - 1)
                elif not self_closing:
                    raw_depth += 1
            out.append(part)
            continue

        if raw_depth or not part:
            out.append(part)
            continue

        prev_info = infos[i - 1] if i > 0 else None
        next_info = infos[i + 1] if i + 1 < len(parts) else None

        if i == 0 or (prev_info and prev_info[0] in _BLOCK_TAGS):
            part = part.lstrip("\n")
        if i + 1 == len(parts) or (next_info and next_info[0] in _BLOCK_TAGS):
            part = part.rstrip("\n")

        out.append(part.replace("\n", _BR))

    return "".join(out)


# ---------------------------------------------------------------------------
# Rich HTML -> regular Telegram HTML (for send_message)
# ---------------------------------------------------------------------------

_PASSTHROUGH = frozenset({
    "b", "strong", "i", "em", "u", "ins", "s", "strike", "del",
    "tg-spoiler", "code", "pre", "blockquote", "tg-emoji",
})
_ALLOWED_ATTRS = {
    "a": ("href",), "code": ("class",), "pre": ("class",),
    "tg-emoji": ("emoji-id",), "blockquote": ("expandable",),
}
_HEADINGS = frozenset({"h1", "h2", "h3", "h4", "h5", "h6"})
_KEEP_ENTITIES = frozenset({"lt", "gt", "amp", "quot"})


class _Downgrader(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self._out: list[str] = []
        self._stack: list[tuple[str, str, int]] = []  # (tag, close_str, close_newlines)
        self._lists: list[list] = []                  # [ordered, counter]
        self._cells = 0

    def result(self) -> str:
        return "".join(self._out).strip("\n")

    # -- helpers
    def _tail_newlines(self) -> int:
        tail = "".join(self._out[-4:])
        return len(tail) - len(tail.rstrip("\n"))

    def _ensure_newlines(self, n: int):
        if n and self._out:
            missing = n - self._tail_newlines()
            if missing > 0:
                self._out.append("\n" * missing)

    def _in_pre(self) -> bool:
        return any(tag == "pre" for tag, _, _ in self._stack)

    @staticmethod
    def _rebuild(tag: str, attrs: dict[str, str]) -> str:
        parts = [tag]
        for key in _ALLOWED_ATTRS.get(tag, ()):
            if key in attrs:
                value = attrs[key]
                parts.append(key if value == "" else f'{key}="{_html.escape(value, quote=True)}"')
        return "<" + " ".join(parts) + ">"

    # -- parser callbacks
    def handle_starttag(self, tag, attrs):
        self._open(tag, attrs, False)

    def handle_startendtag(self, tag, attrs):
        self._open(tag, attrs, True)

    def handle_endtag(self, tag):
        for i in range(len(self._stack) - 1, -1, -1):
            if self._stack[i][0] == tag:
                while len(self._stack) > i:      # also closes unclosed inner tags (<li>, <p>)
                    self._close(self._stack.pop())
                break

    def handle_data(self, data):
        if not self._in_pre():
            if not self._out:
                data = data.lstrip()
            elif self._tail_newlines():
                data = data.lstrip("\n ")
        if data:
            self._out.append(data)

    def handle_entityref(self, name):
        if name in _KEEP_ENTITIES:
            self._out.append(f"&{name};")
        else:  # &nbsp; &hellip; &mdash; ... are not supported in regular HTML
            self._out.append(_html.escape(_html.unescape(f"&{name};"), quote=False))

    def handle_charref(self, name):
        self._out.append(f"&#{name};")

    def close(self):
        super().close()
        while self._stack:
            self._close(self._stack.pop())

    # -- translation
    def _open(self, tag: str, attrs_list, self_closing: bool):
        attrs = {k: (v or "") for k, v in attrs_list}

        if tag == "br":
            self._out.append("\n")
            return
        if tag == "hr":
            self._ensure_newlines(2)
            self._out.append("――――――――")
            self._ensure_newlines(2)
            return
        if tag in ("img", "tg-map"):
            return

        open_nl, open_str, close_str, close_nl = 0, "", "", 0

        if tag in _PASSTHROUGH:
            open_str, close_str = self._rebuild(tag, attrs), f"</{tag}>"
        elif tag in _HEADINGS:
            open_nl, open_str, close_str, close_nl = 2, "<b>", "</b>", 2
        elif tag in ("p", "figure", "table"):
            open_nl, close_nl = 2, 2
        elif tag == "footer":
            open_nl, open_str, close_str, close_nl = 2, "<i>", "</i>", 2
        elif tag == "aside":
            open_nl, open_str, close_str, close_nl = 2, "<blockquote>", "</blockquote>", 1
        elif tag in ("figcaption", "caption"):
            open_nl, open_str, close_str, close_nl = 1, "<i>", "</i>", 1
        elif tag == "cite":
            open_nl, open_str, close_nl = 1, "— ", 1
        elif tag == "summary":
            open_nl, open_str, close_str, close_nl = 2, "<b>", "</b>", 1
        elif tag == "details":
            open_nl, close_nl = 2, 1
        elif tag == "tr":
            open_nl, close_nl = 1, 1
            self._cells = 0
        elif tag in ("td", "th"):
            open_str = (" | " if self._cells else "") + ("<b>" if tag == "th" else "")
            close_str = "</b>" if tag == "th" else ""
            self._cells += 1
        elif tag in ("ul", "ol"):
            try:
                start = int(attrs.get("start", 1))
            except ValueError:
                start = 1
            self._lists.append([tag == "ol", start - 1])
            open_nl, close_nl = 1, 1
        elif tag == "li":
            indent = "  " * max(len(self._lists) - 1, 0)
            if self._lists and self._lists[-1][0]:
                value = attrs.get("value", "")
                if value.lstrip("-").isdigit():
                    self._lists[-1][1] = int(value)
                else:
                    self._lists[-1][1] += 1
                open_str = f"{indent}{self._lists[-1][1]}. "
            else:
                open_str = f"{indent}• "
            open_nl, close_nl = 1, 1
        elif tag == "tg-math-block":
            open_nl, open_str, close_str, close_nl = 2, "<pre>", "</pre>", 2
        elif tag == "tg-math":
            open_str, close_str = "<code>", "</code>"
        elif tag == "a":
            href = attrs.get("href", "")
            if "name" not in attrs and href and not href.startswith("#"):
                open_str, close_str = self._rebuild(tag, attrs), "</a>"
        # everything else (mark, sub, sup, tg-time, tg-reference, collage, video, ...):
        # the tag is dropped, the content is kept

        self._ensure_newlines(open_nl)
        if open_str:
            self._out.append(open_str)

        entry = (tag, close_str, close_nl)
        if self_closing:
            self._close(entry)
        else:
            self._stack.append(entry)

    def _close(self, entry: tuple[str, str, int]):
        tag, close_str, close_nl = entry
        if close_str:
            self._out.append(close_str)
        if tag in ("ul", "ol") and self._lists:
            self._lists.pop()
        self._ensure_newlines(close_nl)


def downgrade_rich_html(text: str) -> str:
    """Converts Rich HTML into HTML accepted by regular `send_message`."""
    try:
        parser = _Downgrader()
        parser.feed(text)
        parser.close()
        return parser.result()
    except Exception:
        return _TAG_RE.sub(
            lambda m: "" if m.group(1).lower() in RICH_ONLY_TAGS else m.group(0), text
        )