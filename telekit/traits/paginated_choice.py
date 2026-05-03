from typing import Callable, Any, Iterable

import telekit
from dataclasses import dataclass

@dataclass
class _NavButton:
    start_index: int

class PaginatedChoice(telekit.Handler):

    # ── entry point ───────────────────────────────────────────────

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    PAGINATED_CHOICE_BACK_LABEL: str = "« Back"
    PAGINATED_CHOICE_NEXT_LABEL: str = "Next »"
    PAGINATED_CHOICE_PAGE_LABEL: str | None = "({page}/{pages})"  # use .format(page=..., pages=...)

    def paginated_choice[T](self, choices: dict[str, T] | Iterable[T], on_choice: Callable[[T], Any], on_update: Callable[[], Any] | None = None, row_width: int = 1, page_size: int = 10) -> None:
        """
        Display a paginated inline keyboard for choosing from a list of items.

        Navigation buttons (``« Back``, ``Next »``) are added automatically
        when the item count exceeds ``page_size``. If only one item is present,
        ``on_choice`` is called immediately without rendering a keyboard.

        :param choices: Items to display. Accepts a ``dict[str, T]`` (label: value),
                        or any ``Iterable[T]``.
        :type choices: ``dict[str, T] | Iterable[T]``
        :param on_choice: Callback invoked with the selected value.
        :type on_choice: ``Callable[[T], Any]``
        :param on_update: Optional callback invoked before each page render.
                        Useful for updating entry text.
        :type on_update: ``Callable[[], Any] | None``
        :param row_width: Number of choice buttons per row. Defaults to ``1``.
        :type row_width: ``int``
        :param page_size: Maximum number of items per page. Defaults to ``10``.
        :type page_size: ``int``

        Example::

            self.paginated_choice(
                choices="ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                on_choice=self.handle_letter,
                on_update=lambda: self.chain.set_entry_text(self.handle_letter),
                row_width=5,
            )
        """
        if isinstance(choices, dict):
            _choices: dict[str, T] = choices.copy() # pyright: ignore[reportAssignmentType]
        else:
            _choices: dict[str, T] = {str(c): c for c in choices}

        if len(_choices) == 1:
            on_choice(next(iter(_choices.values())))
            return
        
        self._paginated_choice(0, _choices, on_choice, on_update, row_width, page_size)

    def _paginated_choice[T](self, start: int, choices: dict[str, T], on_choice: Callable[[T], Any], on_update: Callable[[], Any] | None, row_width: int, page_size: int) -> None:
        total = len(choices)
        
        page  = start // page_size + 1
        pages = (total + page_size - 1) // page_size
        page_items = list(choices.items())[start : start + page_size]

        if on_update is not None:
            on_update()

        keyboard: dict[str, T | _NavButton] = {}
        keyboard.update(page_items)

        # navigation row
        has_back = start - page_size >= 0
        has_next = start + page_size < total

        nav: dict[str, T | _NavButton] = {}

        if has_back:
            nav[self.PAGINATED_CHOICE_BACK_LABEL] = \
                _NavButton(start - page_size)
        if has_back and has_next and self.PAGINATED_CHOICE_PAGE_LABEL:
            nav[self.PAGINATED_CHOICE_PAGE_LABEL.format(page=page, pages=pages)] = \
                _NavButton(start)
        if has_next:
            nav[self.PAGINATED_CHOICE_NEXT_LABEL] = \
                _NavButton(start + page_size)

        # each choice on its own row, nav row at the end
        choices_count  = len(keyboard)
        nav_count      = len(nav)
        
        full_rows = choices_count // row_width
        remainder = choices_count % row_width

        if remainder > 0:
            _row_width = (*([row_width] * full_rows), remainder, nav_count)
        else:
            _row_width = (*([row_width] * full_rows), nav_count)

        keyboard.update(nav)

        def _on_choice(choice: T | _NavButton):
            if isinstance(choice, _NavButton):
                self._paginated_choice(choice.start_index, choices, on_choice, on_update, row_width, page_size)
            else:
                on_choice(choice)

        self.chain.set_inline_choice(
            _on_choice,
            keyboard,
            row_width=_row_width,
        )
        self.chain.edit()