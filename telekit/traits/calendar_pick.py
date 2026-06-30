"""
telekit calendar trait — interactive inline date picker.

Usage::

    class BookingHandler(CalendarPick, telekit.Handler):

        def handle(self) -> None:
            self.calendar_pick(
                on_date=self._on_date_picked,
                year_range=(2000, datetime.date.today().year),
            )

        def _on_date_picked(self, date: datetime.date) -> None:
            ...


Locking modes
-------------
``locked_month=(year, month)``
    User only picks the day — no navigation shown.
``locked_year=year``
    User picks month then day within the given year.
``year_range=(min_year, max_year)``
    Free navigation restricted to the given year span.

Initial view
------------
``initial=None``            current month (default)
``initial=datetime.date``   that month
``initial=int``             that year's month-grid
Ignored when ``locked_month`` is provided.

Navigation hints
----------------
``show_nav_hints=True``
    Arrow buttons show neighbouring labels:
    ``< Apr`` / ``Jun >``  in month view,
    ``< 2024`` / ``2026 >``  in year/decade view.
``show_nav_hints=False``
    Plain ``<`` / ``>`` arrows (default).
"""
from __future__ import annotations

import calendar
import datetime
import re
from dataclasses import dataclass, field
from typing import Callable

import telekit
from telekit.types import InlineKeyboard

__all__ = ["CalendarPick"]

# ---------------------------------------------------------------------------
# Display constants
# ---------------------------------------------------------------------------

_WEEKDAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
_MONTHS   = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
             "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

_BLANK = " "

# Module-level Calendar instance (Monday-first) — created once, reused everywhere.
_CAL = calendar.Calendar(firstweekday=0)

# Number of years shown per page in the decade picker.
_DECADE_SIZE = 10


# ---------------------------------------------------------------------------
# Picker context
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class _Ctx:
    """
    Immutable snapshot of all picker constraints passed between view renderers.

    All constraint checks must go through the helpers defined below so that
    no view can accidentally bypass locking rules.

    :param on_date: Callback fired when the user confirms a day.
    :param locked_month: ``(year, month)`` pair that pins the picker to a
        single month; navigation is hidden entirely.
    :param locked_year: Year that pins the picker to a single year; the user
        may choose any month within that year.
    :param min_year: Lower bound of the allowed year range (inclusive).
    :param max_year: Upper bound of the allowed year range (inclusive).
    :param show_nav_hints: When ``True`` arrow labels include the neighbour
        value (e.g. ``< Apr`` or ``2026 >``).
    """

    on_date:        Callable[[datetime.date], None]
    locked_month:   tuple[int, int] | None
    locked_year:    int | None
    min_year:       int | None
    max_year:       int | None
    show_nav_hints: bool = field(default=False)

    # ------------------------------------------------------------------
    # Constraint helpers — all locking logic lives here
    # ------------------------------------------------------------------

    def year_allowed(self, year: int) -> bool:
        """Return ``True`` when *year* is within the permitted range."""
        if self.locked_year is not None and year != self.locked_year:
            return False
        if self.min_year is not None and year < self.min_year:
            return False
        if self.max_year is not None and year > self.max_year:
            return False
        return True

    def month_allowed(self, year: int, month: int) -> bool:
        """Return ``True`` when *(year, month)* is reachable by the user."""
        if not self.year_allowed(year):
            return False
        if self.locked_month is not None and (year, month) != self.locked_month:
            return False
        return True

    def date_allowed(self, date: datetime.date) -> bool:
        """Return ``True`` when *date* is a valid pick given all constraints."""
        return self.month_allowed(date.year, date.month)

    def clamp_year(self, year: int) -> int:
        """Return *year* clamped to ``[min_year, max_year]``."""
        if self.min_year is not None and year < self.min_year:
            return self.min_year
        if self.max_year is not None and year > self.max_year:
            return self.max_year
        return year


# ---------------------------------------------------------------------------
# Date text parser
# ---------------------------------------------------------------------------

_RE_YMD = re.compile(r"^(\d{4})[.\-](\d{1,2})[.\-](\d{1,2})$")
_RE_YM  = re.compile(r"^(\d{4})[.\-](\d{1,2})$")
_RE_Y   = re.compile(r"^(\d{4})$")


def _parse(text: str) -> tuple[int, int | None, int | None] | None:
    """
    Parse user-typed date text into ``(year, month, day)``.

    Accepted formats (separator is ``.`` or ``-``):

    =========  =========================
    YYYY       ``(year, None, None)``
    YYYY.MM    ``(year, month, None)``
    YYYY.MM.DD ``(year, month, day)``
    =========  =========================

    :param text: Raw text entered by the user.
    :returns: A three-tuple on success, ``None`` on any parse or validation
        failure so callers can silently discard bad input.
    """
    t = text.strip()

    m = _RE_YMD.match(t)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            datetime.date(y, mo, d)
        except ValueError:
            return None
        return y, mo, d

    m = _RE_YM.match(t)
    if m:
        y, mo = int(m.group(1)), int(m.group(2))
        if not 1 <= mo <= 12:
            return None
        return y, mo, None

    m = _RE_Y.match(t)
    if m:
        return int(m.group(1)), None, None

    return None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _shift(year: int, month: int, delta: int) -> tuple[int, int]:
    """
    Add *delta* months to *(year, month)* and return the normalised result.

    :param year: Current year.
    :param month: Current month (1–12).
    :param delta: Number of months to advance (positive) or retreat (negative).
    :returns: Normalised ``(year, month)`` tuple.
    """
    month += delta
    if month < 1:
        return year - 1, 12
    if month > 12:
        return year + 1, 1
    return year, month


def _decade_start(year: int) -> int:
    """
    Return the first year of the decade-picker page that contains *year*.

    Pages are aligned to multiples of :data:`_DECADE_SIZE`
    (e.g. 2020–2029 for any year in that range).

    :param year: Any year within the desired page.
    :returns: First year of the containing page.
    """
    return (year // _DECADE_SIZE) * _DECADE_SIZE


# ---------------------------------------------------------------------------
# Trait
# ---------------------------------------------------------------------------

class CalendarPick(telekit.Trait):
    """
    Inline calendar date-picker mixin.

    Mix into any :class:`telekit.Handler` subclass and call
    :meth:`calendar_pick` to start the interaction.  See the module docstring
    for full usage examples and locking-mode documentation.
    """

    # -----------------------------------------------------------------------
    # Public entry point
    # -----------------------------------------------------------------------

    def calendar_pick(
        self,
        on_date: Callable[[datetime.date], None],
        *,
        initial:        datetime.date | int | None = None,
        locked_month:   tuple[int, int] | None = None,
        locked_year:    int | None = None,
        year_range:     tuple[int, int] | None = None,
        show_nav_hints: bool = False,
    ) -> None:
        """
        Open the calendar picker.

        :param on_date: Called with the selected :class:`datetime.date` when
            the user taps a day button.
        :param initial: Starting view.  :class:`datetime.date` opens that
            month; :class:`int` opens the month-grid for that year; ``None``
            uses the current month (default).  Ignored when *locked_month* is
            provided.
        :param locked_month: ``(year, month)`` — restrict to a single month;
            the user only picks the day and all navigation is hidden.
        :param locked_year: Restrict navigation to a single year; year arrows
            and the decade picker are hidden.
        :param year_range: ``(min_year, max_year)`` — constrain free
            navigation to this inclusive year span.
        :param show_nav_hints: When ``True`` navigation arrows include the
            neighbour label, e.g. ``< Apr`` or ``2026 >``.
        """
        min_yr = year_range[0] if year_range else None
        max_yr = year_range[1] if year_range else None

        ctx = _Ctx(
            on_date=on_date,
            locked_month=locked_month,
            locked_year=locked_year,
            min_year=min_yr,
            max_year=max_yr,
            show_nav_hints=show_nav_hints,
        )

        # locked_month overrides everything — jump straight to day picker.
        if locked_month:
            self.__calendar_pick_month_view(*locked_month, ctx=ctx)
            return

        # locked_year — open that year's month grid.
        if locked_year is not None:
            self.__calendar_pick_year_view(ctx.clamp_year(locked_year), ctx=ctx)
            return

        # Explicit month initial.
        if isinstance(initial, datetime.date):
            self.__calendar_pick_month_view(ctx.clamp_year(initial.year), initial.month, ctx=ctx)
            return

        # Explicit year initial — show month grid.
        if isinstance(initial, int):
            self.__calendar_pick_year_view(ctx.clamp_year(initial), ctx=ctx)
            return

        # Default: current month.
        today = datetime.date.today()
        self.__calendar_pick_month_view(ctx.clamp_year(today.year), today.month, ctx=ctx)

    # -----------------------------------------------------------------------
    # Navigation guards
    # -----------------------------------------------------------------------
    #
    # These re-check constraints at press time (defense in depth) before
    # delegating to the corresponding *_view renderer — mirroring what the
    # old centralised `_choice` dispatcher used to do.

    def __calendar_pick_pick(self, date: datetime.date, *, ctx: _Ctx) -> None:
        """Fire the user-supplied callback for *date*, if still allowed."""
        if not ctx.date_allowed(date):
            return
        try:
            ctx.on_date(date)
        except Exception:
            pass

    def __calendar_pick_goto_month(self, year: int, month: int, *, ctx: _Ctx) -> None:
        """Navigate to the day picker for *(year, month)*, if allowed."""
        if ctx.month_allowed(year, month):
            self.__calendar_pick_month_view(year, month, ctx=ctx)

    def __calendar_pick_goto_year(self, year: int, *, ctx: _Ctx) -> None:
        """Navigate to the month picker for *year*, if allowed."""
        if ctx.year_allowed(year):
            self.__calendar_pick_year_view(year, ctx=ctx)

    def __calendar_pick_goto_decade(self, first_year: int, *, ctx: _Ctx) -> None:
        """Navigate to the decade page starting at *first_year*."""
        self.__calendar_pick_decade_view(first_year, ctx=ctx)

    # -----------------------------------------------------------------------
    # Month view  (day picker)
    # -----------------------------------------------------------------------

    def __calendar_pick_month_view(self, year: int, month: int, *, ctx: _Ctx) -> None:
        """
        Render the day-picker grid for *(year, month)*.

        Layout (top to bottom):

        * Month button | Year button  (static when locked)
        * Weekday labels row
        * Day grid (up to 6 rows x 7 columns)
        * Navigation row: ``«`` [ ``This month`` ] ``»``
          Hidden when ``locked_month`` is set.
          The centre button appears only when the displayed month differs from
          the current calendar month; it navigates to the current month.

        :param year: Year of the month being displayed.
        :param month: Month being displayed (1-12).
        :param ctx: Immutable picker context carrying all constraints.
        """
        today  = datetime.date.today()
        locked = ctx.locked_month is not None

        kb = InlineKeyboard()

        # -- Header: two separate buttons for month and year -----------------
        # Month button opens the year-view (month selector) unless fully locked.
        # Year button opens the decade picker unless year navigation is locked.
        month_label = _MONTHS[month - 1].upper()
        year_label  = str(year)

        kb.row()
        if locked:
            kb.add_static(month_label)
            kb.add_static(year_label)
        else:
            kb.add_callback(
                month_label, self.__calendar_pick_goto_year,
                pass_args=(year,), pass_kwargs={"ctx": ctx},
            )
            if ctx.locked_year is None:
                kb.add_callback(
                    year_label, self.__calendar_pick_goto_decade,
                    pass_args=(_decade_start(year),), pass_kwargs={"ctx": ctx},
                )
            else:
                kb.add_static(year_label)

        # -- Weekday labels row ----------------------------------------------
        kb.row()
        for label in _WEEKDAYS:
            kb.add_static(label)

        # -- Day grid --------------------------------------------------------
        kb.grid(7)
        blanks = 0
        for week in _CAL.monthdayscalendar(year, month):
            for day in week:
                if day == 0:
                    blanks += 1
                    kb.add_static(_BLANK * blanks)
                else:
                    date = datetime.date(year, month, day)
                    is_today: bool = date == today
                    label: str = f"·{day}·" if is_today else str(day)
                    kb.add_callback(
                        label, self.__calendar_pick_pick,
                        pass_args=(date,), pass_kwargs={"ctx": ctx},
                        style="danger" if is_today else None
                    )
        kb.grid_end()

        # -- Navigation row --------------------------------------------------
        if not locked:
            prev_y, prev_m = _shift(year, month, -1)
            next_y, next_m = _shift(year, month, +1)

            can_prev = ctx.month_allowed(prev_y, prev_m)
            can_next = ctx.month_allowed(next_y, next_m)

            if ctx.show_nav_hints:
                prev_label = f"« {_MONTHS[prev_m - 1]}"
                next_label = f"{_MONTHS[next_m - 1]} »"
            else:
                prev_label = "«"
                next_label = "»"

            kb.row()

            if can_prev:
                kb.add_callback(
                    prev_label, self.__calendar_pick_goto_month,
                    pass_args=(prev_y, prev_m), pass_kwargs={"ctx": ctx},
                )
            else:
                kb.add_static(prev_label)

            # Centre button: absent on the current month; otherwise leads to it.
            is_current_month = (year == today.year and month == today.month)
            if not is_current_month:
                if ctx.month_allowed(today.year, today.month):
                    kb.add_callback(
                        "This month", self.__calendar_pick_goto_month,
                        pass_args=(today.year, today.month),
                        pass_kwargs={"ctx": ctx},
                    )
                else:
                    kb.add_static("This month")

            if can_next:
                kb.add_callback(
                    next_label, self.__calendar_pick_goto_month,
                    pass_args=(next_y, next_m), pass_kwargs={"ctx": ctx},
                )
            else:
                kb.add_static(next_label)

        # -- Text-entry handler ----------------------------------------------

        def _entry(text: str) -> None:
            """
            Handle a date typed directly into the message box.

            Invalid, out-of-range, or lock-violating input is silently ignored
            so the current view remains intact.

            :param text: Raw text from the user's message.
            """
            parsed = _parse(text)
            if parsed is None:
                return

            y, mo, d = parsed

            # Full date typed — validate all constraints then fire callback.
            if mo is not None and d is not None:
                if not ctx.month_allowed(y, mo):
                    return
                try:
                    date = datetime.date(y, mo, d)
                except ValueError:
                    return
                if not ctx.date_allowed(date):
                    return
                try:
                    ctx.on_date(date)
                except Exception:
                    pass
                return

            # Month typed — navigate there if constraints permit.
            if mo is not None:
                if not ctx.month_allowed(y, mo):
                    return
                self.__calendar_pick_month_view(y, mo, ctx=ctx)
                return

            # Year typed — navigate if year nav is available.
            if locked or ctx.locked_year is not None:
                return
            if not ctx.year_allowed(y):
                return
            self.__calendar_pick_year_view(ctx.clamp_year(y), ctx=ctx)

        # -- Compose & render ------------------------------------------------

        self.chain.set_keyboard(kb)
        self.chain.set_entry_text(_entry, delete_user_response=True)
        self.chain.edit()

    # -----------------------------------------------------------------------
    # Year view  (month selector for a given year)
    # -----------------------------------------------------------------------

    def __calendar_pick_year_view(self, year: int, *, ctx: _Ctx) -> None:
        """
        Render the month-selector grid for *year*.

        Layout:

        * Year button (opens decade picker; static when year nav is locked)
        * Month grid (3 columns x 4 rows); current month highlighted when
          *year* equals the current calendar year; disabled months are static
        * Navigation row: ``«`` [ ``This year`` ] ``»``
          Hidden when ``locked_year`` is set.
          The centre button appears only when the displayed year differs from
          the current calendar year; it navigates back to the current year.

        :param year: The year whose months are being listed.
        :param ctx: Immutable picker context carrying all constraints.
        """
        today = datetime.date.today()

        kb = InlineKeyboard()

        # -- Header: year button opens decade picker if year nav is free -----
        kb.row()
        if ctx.locked_year is not None:
            kb.add_static(str(year))
        else:
            kb.add_callback(
                str(year), self.__calendar_pick_goto_decade,
                pass_args=(_decade_start(year),), pass_kwargs={"ctx": ctx},
            )

        # -- Month grid ------------------------------------------------------
        # Current month is highlighted with centre dots when year matches today.
        # Months outside the allowed range become static (unclickable).
        kb.grid(3)
        for i, name in enumerate(_MONTHS):
            m     = i + 1
            is_current = (year == today.year and m == today.month)
            label = f"·{name}·" if is_current else name
            if ctx.month_allowed(year, m):
                kb.add_callback(
                    label, self.__calendar_pick_goto_month,
                    pass_args=(year, m), pass_kwargs={"ctx": ctx},
                    style="danger" if is_current else None
                )
            else:
                kb.add_static(label, style="danger" if is_current else None)
        kb.grid_end()

        # -- Navigation row --------------------------------------------------
        if ctx.locked_year is None:
            can_prev = ctx.year_allowed(year - 1)
            can_next = ctx.year_allowed(year + 1)

            if ctx.show_nav_hints:
                prev_label = f"« {year - 1}"
                next_label = f"{year + 1} »"
            else:
                prev_label = "«"
                next_label = "»"

            kb.row()

            if can_prev:
                kb.add_callback(
                    prev_label, self.__calendar_pick_goto_year,
                    pass_args=(year - 1,), pass_kwargs={"ctx": ctx},
                )
            else:
                kb.add_static(prev_label)

            # Centre button: absent on the current year; otherwise leads to it.
            if year != today.year:
                if ctx.year_allowed(today.year):
                    kb.add_callback(
                        "This year", self.__calendar_pick_goto_year,
                        pass_args=(today.year,), pass_kwargs={"ctx": ctx},
                    )
                else:
                    kb.add_static("This year")

            if can_next:
                kb.add_callback(
                    next_label, self.__calendar_pick_goto_year,
                    pass_args=(year + 1,), pass_kwargs={"ctx": ctx},
                )
            else:
                kb.add_static(next_label)

        # -- Text-entry handler ----------------------------------------------

        def _entry(text: str) -> None:
            """
            Handle a date or year typed directly into the message box.

            Out-of-range or lock-violating input is silently ignored.

            :param text: Raw text from the user's message.
            """
            parsed = _parse(text)
            if parsed is None:
                return

            y, mo, d = parsed

            # Full date — fire callback if everything is allowed.
            if mo is not None and d is not None:
                if not ctx.month_allowed(y, mo):
                    return
                try:
                    date = datetime.date(y, mo, d)
                except ValueError:
                    return
                if not ctx.date_allowed(date):
                    return
                try:
                    ctx.on_date(date)
                except Exception:
                    pass
                return

            # Month typed — navigate if allowed.
            if mo is not None:
                if not ctx.month_allowed(y, mo):
                    return
                self.__calendar_pick_month_view(y, mo, ctx=ctx)
                return

            # Year typed — navigate within constraints.
            if not ctx.year_allowed(y):
                return
            self.__calendar_pick_year_view(ctx.clamp_year(y), ctx=ctx)

        # -- Compose & render ------------------------------------------------

        self.chain.set_keyboard(kb)
        self.chain.set_entry_text(_entry, delete_user_response=True)
        self.chain.edit()

    # -----------------------------------------------------------------------
    # Decade view  (year picker — 10 years, 2 columns x 5 rows)
    # -----------------------------------------------------------------------

    def __calendar_pick_decade_view(self, first_year: int, *, ctx: _Ctx) -> None:
        """
        Render a decade-page picker showing ten consecutive years.

        Layout:

        * Static header showing the page range, e.g. ``2020 - 2029``
        * Year grid (2 columns x 5 rows); current year highlighted with centre
          dots; years outside the allowed range are shown as static buttons
        * Navigation row: ``«`` [ ``This decade`` ] ``»``
          Hidden when year navigation is fully locked.
          The centre button appears only when the displayed page does not
          contain the current year; it navigates back to the current decade.

        :param first_year: First year of the page (should be a multiple of
            :data:`_DECADE_SIZE` for clean alignment).
        :param ctx: Immutable picker context carrying all constraints.
        """
        today     = datetime.date.today()
        last_year = first_year + _DECADE_SIZE - 1

        kb = InlineKeyboard()

        # -- Header ----------------------------------------------------------
        kb.row()
        kb.add_static(f"{first_year} – {last_year}")

        # -- Year grid (2 x 5) -----------------------------------------------
        kb.grid(2)
        for y in range(first_year, first_year + _DECADE_SIZE):
            is_current = y == today.year
            label = f"·{y}·" if is_current else str(y)
            if ctx.year_allowed(y):
                kb.add_callback(
                    label, self.__calendar_pick_goto_year,
                    pass_args=(y,), pass_kwargs={"ctx": ctx},
                    style="danger" if is_current else None
                )
            else:
                kb.add_static(label, style="danger" if is_current else None)
        kb.grid_end()

        # -- Navigation row --------------------------------------------------
        if ctx.locked_year is None:
            prev_first = first_year - _DECADE_SIZE
            next_first = first_year + _DECADE_SIZE

            # A page is reachable when at least one year on it is allowed.
            def _page_reachable(pf: int) -> bool:
                return any(ctx.year_allowed(y) for y in range(pf, pf + _DECADE_SIZE))

            can_prev = _page_reachable(prev_first)
            can_next = _page_reachable(next_first)

            if ctx.show_nav_hints:
                prev_label = f"« {prev_first}s"
                next_label = f"{next_first}s »"
            else:
                prev_label = "«"
                next_label = "»"

            this_decade_first = _decade_start(today.year)

            kb.row()

            if can_prev:
                kb.add_callback(
                    prev_label, self.__calendar_pick_goto_decade,
                    pass_args=(prev_first,), pass_kwargs={"ctx": ctx},
                )
            else:
                kb.add_static(prev_label)

            # Centre button: absent when already on the current decade page.
            if this_decade_first != first_year:
                if _page_reachable(this_decade_first):
                    kb.add_callback(
                        "This decade", self.__calendar_pick_goto_decade,
                        pass_args=(this_decade_first,), pass_kwargs={"ctx": ctx},
                    )
                else:
                    kb.add_static("This decade")

            if can_next:
                kb.add_callback(
                    next_label, self.__calendar_pick_goto_decade,
                    pass_args=(next_first,), pass_kwargs={"ctx": ctx},
                )
            else:
                kb.add_static(next_label)

        # -- Text-entry handler ----------------------------------------------

        def _entry(text: str) -> None:
            """
            Handle a date or year typed directly into the message box.

            Out-of-range or lock-violating input is silently ignored.

            :param text: Raw text from the user's message.
            """
            parsed = _parse(text)
            if parsed is None:
                return

            y, mo, d = parsed

            # Full date — fire callback if everything is allowed.
            if mo is not None and d is not None:
                if not ctx.month_allowed(y, mo):
                    return
                try:
                    date = datetime.date(y, mo, d)
                except ValueError:
                    return
                if not ctx.date_allowed(date):
                    return
                try:
                    ctx.on_date(date)
                except Exception:
                    pass
                return

            # Month typed — navigate there if allowed.
            if mo is not None:
                if not ctx.month_allowed(y, mo):
                    return
                self.__calendar_pick_month_view(y, mo, ctx=ctx)
                return

            # Year typed — navigate within constraints.
            if not ctx.year_allowed(y):
                return
            self.__calendar_pick_year_view(ctx.clamp_year(y), ctx=ctx)

        # -- Compose & render ------------------------------------------------

        self.chain.set_keyboard(kb)
        self.chain.set_entry_text(_entry, delete_user_response=True)
        self.chain.edit()