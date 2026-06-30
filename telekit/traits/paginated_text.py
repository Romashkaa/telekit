from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Any, Iterable

import telekit
from telekit.utils import compose_keyboard
from telekit.html_text import HTMLText
from telekit.styles import Raw

_TG_MAX_CHARS    = 4096
_ELLIPSIS_TOP    = ""
_ELLIPSIS_BOTTOM = "…"

# Window for PaginatedText: int >= 0
#   0   -> [size, size]       exact hard cut
#   N>0 -> [size-N, size]     up to N shorter
PaginatedWindow = int


@dataclass
class _TextPaginationConfig:
    chunk:          int
    window:         PaginatedWindow
    page_label:     str | None
    back_label:     str
    next_label:     str
    header:         str
    footer:         str
    show_ellipsis:  bool
    too_long_label: str | None


@dataclass
class _NavButton:
    page_index: int


@dataclass
class _PageViewButton:
    """Sentinel: clicking the page indicator opens the page picker."""
    pass


@dataclass
class _GoPage:
    index: int

@dataclass
class _ShiftWindow:
    delta: int   # -10 or +10


def _sender_text_len(sender: Any) -> int:
    """Return `len(sender._title + sender._additional)` safely."""
    title = Raw(sender._title     ).html
    end   = Raw(sender._additional).html
    return len(title) + len(end) + 2 # "\n\n" separator


def _effective_chunk(raw_chunk: int, sender: Any) -> int:
    """Clamp *raw_chunk* so it never exceeds TG limit minus sender prefix."""
    prefix = _sender_text_len(sender)
    return max(1, min(raw_chunk, _TG_MAX_CHARS - prefix))


def _split_text(text: str, cfg: _TextPaginationConfig, chunk: int) -> list[str]:
    """Split plain HTML text into pages using HTMLText.chunk."""
    worst_overhead = (
        len(cfg.header) + len(cfg.footer)
        + (len(_ELLIPSIS_TOP) + 1 + len(_ELLIPSIS_BOTTOM) + 1)
        if cfg.show_ellipsis else
        len(cfg.header) + len(cfg.footer)
    )
    effective = max(1, chunk - worst_overhead)
    window: int | tuple[int, int] = cfg.window if cfg.window > 0 else 0

    pages = list(HTMLText(text).chunk(
        effective,
        split_at=(",", ".", "!", "?", "\n", " "),
        window=window,
    ))
    return [str(p).strip() for p in pages]


def _split_items(
    items: list[str],
    cfg: _TextPaginationConfig,
    chunk: int,
) -> list[str]:
    """
    Validate each item fits in a page (with worst-case header/footer/ellipsis).
    Items that are too long are split further using the same window rules.
    """
    worst_overhead = (
        len(cfg.header) + len(cfg.footer)
        + (len(_ELLIPSIS_TOP) + 1 + len(_ELLIPSIS_BOTTOM) + 1)
        if cfg.show_ellipsis else
        len(cfg.header) + len(cfg.footer)
    )
    max_item = max(1, chunk - worst_overhead)

    window: int | tuple[int, int] = cfg.window if cfg.window > 0 else 0

    result: list[str] = []
    for item in items:
        if len(HTMLText(item)) <= max_item:
            result.append(item)
        else:
            sub = HTMLText(item).chunk(
                max_item,
                split_at=(",", ".", "!", "?", "\n", " "),
                window=window,
            )
            result.extend(str(p).strip() for p in sub)
    return result


def _hard_truncate(text: str, max_visible: int) -> str:
    """Remove trailing visible chars until len(HTMLText(text)) <= max_visible."""
    h = HTMLText(text)
    if len(h) <= max_visible:
        return text
    return str(h[:max_visible])


class PaginatedText(telekit.Trait):
    """
    A trait that adds paginated text display to any handler.

    Accepts either a plain HTML string **or** an ``Iterable[str]`` (list of
    items, one per page).  Navigation supports « / » buttons for ±10 pages
    and a page-picker overlay when the user taps the ``{page}/{pages}``
    indicator.

    **Class attributes (override per subclass):**

    .. list-table::
        :widths: 30 70

        * - ``PAGINATED_TEXT_BACK_LABEL``
          - Label for the `←` button.  Default: ``« Back``.
        * - ``PAGINATED_TEXT_NEXT_LABEL``
          - Label for the `→` button.  Default: ``Next »``.
        * - ``PAGINATED_TEXT_PAGE_LABEL``
          - Template for the page indicator (``{page}`` / ``{pages}``).
            ``None`` hides it.  Default: ``{page} / {pages}``.
        * - ``PAGINATED_TEXT_TOO_LONG``
          - Message shown in place of an item that is too long to display
            **and** ``allow_split=False``.  ``None`` falls back to truncation.
            Default: ``None``.
    """

    PAGINATED_TEXT_BACK_LABEL: str        = "« Back"
    PAGINATED_TEXT_NEXT_LABEL: str        = "Next »"
    PAGINATED_TEXT_PAGE_LABEL: str | None = "{page} / {pages}"
    PAGINATED_TEXT_TOO_LONG:   str | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def paginated_text(
        self,
        text: str | Iterable[str],
        *,
        chunk:        int                      = _TG_MAX_CHARS,
        window:       PaginatedWindow          = 10,
        page_label:   str | None               = ...,   # type: ignore[assignment]
        back_label:   str | None               = None,
        next_label:   str | None               = None,
        header:       str                      = "",
        footer:       str                      = "",
        show_ellipsis: bool                    = True,
        allow_split:  bool                     = True,
        on_update:    Callable[[], Any] | None = None,
    ) -> None:
        """
        Display long HTML text (or a list of items) split into pages.

        :param text: Full HTML string **or** ``Iterable[str]`` of items
            (one item = one page candidate).
        :param chunk: Target characters per chunk *before* overhead.
            Clamped to ``min(chunk, TG_LIMIT - len(sender._title + sender._additional))``.
        :param window: Allowed shortening window for smart splits.
            ``0`` → exact hard cut.  ``N > 0`` → may be up to N chars shorter.
            *(No "longer" option — unsafe for paginated content.)*
        :param page_label: Override page indicator template.  ``...`` uses the
            class default.  ``None`` hides the indicator.
        :param back_label: Override back button label.
        :param next_label: Override next button label.
        :param header: Text prepended to every page.
        :param footer: Text appended to every page.
        :param show_ellipsis: Prepend/append ``…`` cues at page boundaries.
        :param allow_split: For ``Iterable[str]`` input — if ``True`` (default)
            items that are too long are automatically split.  If ``False`` they
            are replaced with ``PAGINATED_TEXT_TOO_LONG`` (or truncated if that
            is ``None``).
        :param on_update: Callback invoked before each page render.
        """
        if window < 0:
            raise ValueError("PaginatedText window must be >= 0")

        resolved_page_label = (
            self.PAGINATED_TEXT_PAGE_LABEL if page_label is ... else page_label
        )
        resolved_back = back_label or self.PAGINATED_TEXT_BACK_LABEL
        resolved_next = next_label or self.PAGINATED_TEXT_NEXT_LABEL

        sender       = self.chain.sender
        eff_chunk    = _effective_chunk(chunk, sender)

        cfg = _TextPaginationConfig(
            chunk=eff_chunk,
            window=window,
            page_label=resolved_page_label,
            back_label=resolved_back,
            next_label=resolved_next,
            header=header,
            footer=footer,
            show_ellipsis=show_ellipsis,
            too_long_label=self.PAGINATED_TEXT_TOO_LONG,
        )

        # ── build page list ───────────────────────────────────────────────
        if isinstance(text, str):
            pages = _split_text(text, cfg, eff_chunk)
        else:
            raw_items = list(text)
            if allow_split:
                pages = _split_items(raw_items, cfg, eff_chunk)
            else:
                # Replace oversized items
                worst_overhead = (
                    len(header) + len(footer)
                    + (len(_ELLIPSIS_TOP) + 1 + len(_ELLIPSIS_BOTTOM) + 1)
                    if show_ellipsis else len(header) + len(footer)
                )
                max_item = max(1, eff_chunk - worst_overhead)
                pages = []
                for item in raw_items:
                    if len(HTMLText(item)) <= max_item:
                        pages.append(item)
                    elif cfg.too_long_label is not None:
                        pages.append(cfg.too_long_label)
                    else:
                        pages.append(_hard_truncate(item, max_item))

        if not pages:
            return

        if len(pages) == 1:
            body = header + pages[0] + footer
            sender.set_message(Raw(body))
            if on_update is not None:
                on_update()
            self.chain.edit()
            return

        self._paginated_text_render(0, pages, cfg, on_update)

    # ------------------------------------------------------------------
    # Internal rendering
    # ------------------------------------------------------------------

    def _paginated_text_render(
        self,
        page_index: int,
        pages:      list[str],
        cfg:        _TextPaginationConfig,
        on_update:  Callable[[], Any] | None,
    ) -> None:
        if on_update is not None:
            on_update()

        total = len(pages)
        page  = page_index + 1

        has_back = page_index > 0
        has_next = page_index < total - 1

        # ── ellipsis cues ─────────────────────────────────────────────────
        top_ell    = (_ELLIPSIS_TOP    + "\n") if has_back and cfg.show_ellipsis else ""
        bottom_ell = ("\n" + _ELLIPSIS_BOTTOM) if has_next and cfg.show_ellipsis else ""

        # ── safety truncation ─────────────────────────────────────────────
        # sender title/additional may have changed in on_update
        sender      = self.chain.sender
        prefix_len  = _sender_text_len(sender)
        max_visible = _TG_MAX_CHARS - prefix_len
        overhead    = len(cfg.header) + len(cfg.footer) + len(top_ell) + len(bottom_ell)
        chunk_budget = max(0, max_visible - overhead)

        chunk_text = _hard_truncate(pages[page_index], chunk_budget)

        body = cfg.header + top_ell + chunk_text + bottom_ell + cfg.footer
        self.chain.sender.set_message(Raw(body))

        # ── navigation keyboard ───────────────────────────────────────────
        nav: dict[str, Any] = {}

        if has_back:
            nav[cfg.back_label] = _NavButton(page_index - 1)

        if cfg.page_label:
            nav[cfg.page_label.format(page=page, pages=total)] = _PageViewButton()

        if has_next:
            nav[cfg.next_label] = _NavButton(page_index + 1)

        def _on_nav(choice: _NavButton | _PageViewButton) -> None:
            if isinstance(choice, _NavButton):
                self._paginated_text_render(choice.page_index, pages, cfg, on_update)
            else:
                self._paginated_text_page_picker(page_index, pages, cfg, on_update)

        self.chain.set_inline_choice(
            _on_nav,
            *compose_keyboard(nav, widths=(-1,))
        )
        self.chain.edit()

    # ------------------------------------------------------------------
    # Page picker overlay
    # ------------------------------------------------------------------

    def _paginated_text_page_picker(
        self,
        current_index:       int,
        pages:               list[str],
        cfg:                 _TextPaginationConfig,
        on_update:           Callable[[], Any] | None,
        current_page_index:  int | None = None,
    ) -> None:
        """Show a grid of 10 page buttons with « / » for ±10 navigation."""
        if current_page_index is None:
            current_page_index = current_index

        total = len(pages)

        # Determine the start of the current window of 10
        window_start = (current_index // 10) * 10
        window_end   = min(window_start + 10, total)

        has_prev_window = window_start > 0
        has_next_window = window_end < total

        # ── build picker keyboard ─────────────────────────────────────────

        picker: dict[str, Any] = {}

        for i in range(window_start, window_end):
            label = str(i + 1)
            if i == current_page_index:
                label = f"· {label} ·"
            picker[label] = _GoPage(i)

        nav_row: dict[str, Any] = {}
        if has_prev_window:
            nav_row["«"] = _ShiftWindow(-10)
        if has_next_window:
            nav_row["»"] = _ShiftWindow(+10)

        def _on_pick(choice: _GoPage | _ShiftWindow) -> None:
            if isinstance(choice, _GoPage):
                self._paginated_text_render(choice.index, pages, cfg, on_update)
            else:
                new_index = max(0, min(current_index + choice.delta, total - 1))
                self._paginated_text_page_picker(new_index, pages, cfg, on_update, current_page_index)

        # Show header only (no text body) in picker view
        sender = self.chain.sender
        sender.set_message(Raw(cfg.header or " "))

        rows, row_width = compose_keyboard(picker, nav_row, widths=(5, 2))

        self.chain.set_inline_choice(_on_pick, rows, row_width)
        self.chain.edit()