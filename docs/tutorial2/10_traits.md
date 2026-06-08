# Traits

Traits are reusable mixins that extend handler behaviour without modifying the handler itself.
Instead of copying the same logic across handlers, you inherit a trait once and get new methods and properties automatically.

```python
class MyHandler(telekit.traits.PaginatedChoice, telekit.Handler):
    ...
```

Multiple traits can be combined on a single handler:

```python
class MyHandler(TrackHandoffOrigin, PaginatedChoice, telekit.Handler):
    ...
```

> [!NOTE]
> Always place `telekit.Handler` last in the inheritance chain.

## Built-in Traits

<details>
<summary><strong>TrackHandoffOrigin</strong> — tracks which handler transferred control via <code>handoff()</code></summary>

### TrackHandoffOrigin

`TrackHandoffOrigin` adds four members to any handler that inherits it:

| **Member**                   | **Description**                                                                  |
| ---------------------------- | -------------------------------------------------------------------------------- |
| `handoff_origin`             | The handler instance that handed off to this one, or `None` if invoked directly. |
| `is_handed_off`              | `True` if this handler was reached via `handoff()`, `False` otherwise.           |
| `handoff_back()`             | Transfer control back to the origin handler via `self.handoff_origin.handle()`   |
| `handoff_back_or(handler)`   | Like `handoff_back()`, but falls back to `handler` if invoked directly.          |

Set `TRACK_HANDOFF_ORIGIN = False` on any subclass to opt out of tracking.

```python
class MyHandler(TrackHandoffOrigin, telekit.Handler):
    def handle(self):
        ...
        self.chain.set_inline_keyboard({
            "« Back": self.handoff_back_or(StartHandler)
        })
        self.chain.edit()
```

</details>

<details>
<summary><strong>PaginatedChoice</strong> — paginated inline keyboard for choosing from a list</summary>

### PaginatedChoice

Renders a paginated inline keyboard from any dict or iterable.
Navigation buttons (`« Back`, `Next »`) are added automatically.

| **Member**                              | **Description**                          |
| --------------------------------------- | ---------------------------------------- |
| `paginated_choice(choices, on_choice, ...)` | Display a paginated choice keyboard. |
| `PAGINATED_CHOICE_BACK_LABEL`           | Label for the back button. Defaults to `« Back`. |
| `PAGINATED_CHOICE_NEXT_LABEL`           | Label for the next button. Defaults to `Next »`. |
| `PAGINATED_CHOICE_PAGE_LABEL`           | Page indicator template. Supports `{page}` and `{pages}`. Set to `None` to hide. Defaults to `{page} / {pages}`. |

```python
self.chain.sender.set_title("🔤 What is your initial?")
self.chain.sender.set_message("Pick the first letter of your name")
self.chain.sender.set_remove_text(False)
self.paginated_choice(
    choices="ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    on_choice=self.handle_letter,
    row_width=5
)
```

Override labels per handler to localise or restyle navigation:

```python
class MyHandler(PaginatedChoice, telekit.Handler):
    PAGINATED_CHOICE_BACK_LABEL = "⬅️ Previous"
    PAGINATED_CHOICE_NEXT_LABEL = "Next ➡️"
    PAGINATED_CHOICE_PAGE_LABEL = None  # hide page indicator
```

`choices` accepts a `dict[str, T]` or any `Iterable[T]`.
If only one item is present, `on_choice` is called immediately without rendering a keyboard.

<details>
<summary>(Click to see the result)</summary>
<table>
<tr>
<td><img src="https://github.com/Romashkaa/telekit/blob/main/docs/images/paginated_choice.png?raw=true" alt="Example" width="300"></td>
</tr>
</table>
</details>

</details>

<details>
<summary><strong>CalendarPick</strong> — inline date picker with month, year, and decade navigation</summary>

### CalendarPick

Renders a three-view inline date picker: month grid, month picker, decade picker.
Navigation is constrained by locking parameters; keyboard input is supported in all views.

| **Member**                    | **Description**       |
| ----------------------------- | --------------------- |
| `calendar_pick(on_date, ...)` | Open the date picker. |

```python
class BookingHandler(telekit.traits.CalendarPick, telekit.Handler):
    def handle(self) -> None:
        self.chain.sender.set_title("📅 Booking date")
        self.chain.sender.set_message(
            "Please select a convenient booking date using the calendar below:"
        )
        self.chain.sender.set_remove_text(False)
        self.calendar_pick(
            on_date=self._on_date_picked,
            year_range=(2000, datetime.date.today().year),
        )

    def _on_date_picked(self, date: datetime.date) -> None:
        self.chain.sender.set_title("📅 Date selected")
        self.chain.sender.set_message(f"You selected {date.strftime('%d.%m.%Y')}")
        self.chain.edit()
```

<details>
<summary>(Click to see the approximate result)</summary>
<table>
<tr>
<td><img src="https://github.com/Romashkaa/telekit/blob/main/docs/images/calendar.png?raw=true" alt="Example" width="350"></td>
</tr>
</table>
</details>

**Parameters**

| **Param**        | **Type**               | **Description**                                                                                      |
| ---------------- | ---------------------- | ---------------------------------------------------------------------------------------------------- |
| `on_date`        | `callable`             | Called with the selected `datetime.date` when the user taps a day.                                   |
| `initial`        | `date \| int \| None`  | Starting view: a `date` opens that month; an `int` opens that year; `None` uses today (default).     |
| `locked_month`   | `tuple[int, int] \| None` | `(year, month)` — restrict to a single month; all navigation is hidden.                          |
| `locked_year`    | `int \| None`          | Restrict navigation to a single year; year arrows and decade picker are hidden.                      |
| `year_range`     | `tuple[int, int] \| None` | `(min_year, max_year)` — constrain free navigation to this inclusive span.                       |
| `show_nav_hints` | `bool`                 | When `True`, arrow buttons include the neighbour label: `« Apr` / `Jun »`. Defaults to `False`.      |

**Locking modes**

- `locked_month=(year, month)` — user only picks the day; no navigation is shown.
- `locked_year=year` — user picks month then day within the given year.
- `year_range=(min_year, max_year)` — free navigation restricted to the given span.

**Keyboard input**

The user can type a date directly in any view:

| Input          | Action                        |
| -------------- | ----------------------------- |
| `YYYY`         | Navigate to that year         |
| `YYYY.MM`      | Navigate to that month        |
| `YYYY.MM.DD`   | Select that date immediately  |

Separator is `.` or `-`. Values outside the allowed range are silently ignored.

</details>

- To create your own trait, see [Creating Traits](./10_2_creating_traits.md).
