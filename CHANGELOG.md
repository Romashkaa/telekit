## Inline Buttons

| **Name**         | **Description**                                                                 |
| ---------------- | ------------------------------------------------------------------------------- |
| `StaticButton`   | A non-interactive inline button that performs no action when pressed.           |
| `AnswerButton`   | A button that responds to a callback query with a notification or alert without executing custom logic. |

- `AnswerButton` and its subclasses (`AlertButton`, `NotificationButton`) now support the `persistent` parameter (Defauts to `True`):
  - `True` — non-blocking hint (does not affect further interactions)
  - `False` — terminates interaction after click

## Traits

| **Name**                   | **Description**                                                       |
| -------------------------- | --------------------------------------------------------------------- |
| `TrackHandoffOrigin`  | Tracks which handler transferred control to this one via `handoff()`.      |
| `PaginatedChoice`    | Adds a paginated inline keyboard for choosing from a list of items.        |

### TrackHandoffOrigin

`TrackHandoffOrigin` adds three members to any handler that inherits it:

| **Member**          | **Description**                                                                  |
| ------------------- | -------------------------------------------------------------------------------- |
| `handoff_origin`    | The handler instance that handed off to this one, or `None` if invoked directly. |
| `is_handed_off`     | `True` if this handler was reached via `handoff()`, `False` otherwise.           |
| `handoff_back()`    | Transfer control back to the origin handler via `self.handoff_origin.handle()`   |
| `handoff_back_or(handler)` | Like `handoff_back()`, but falls back to `handler` on fail.               |

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

### PaginatedChoice

Renders a paginated inline keyboard from any dict or iterable.
Navigation buttons (`« Back`, `Next »`) are added automatically.

| **Member**           | **Description**                                                              |
| -------------------- | ---------------------------------------------------------------------------- |
| `paginated_choice(choices, on_choice, ...)` | Display a paginated choice keyboard. |
| `PAGINATED_CHOICE_BACK_LABEL` | Label for the back navigation button. Defaults to `« Back`. |
| `PAGINATED_CHOICE_NEXT_LABEL` | Label for the next navigation button. Defaults to `Next »`. |
| `PAGINATED_CHOICE_PAGE_LABEL` | Label template for the page indicator button. Supports `{page}` and `{pages}` placeholders. Set to `None` to hide. Defaults to `{page} / {pages}`. |


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
    PAGINATED_CHOICE_BACK_LABEL = "⬅️ Назад"
    PAGINATED_CHOICE_NEXT_LABEL = "Далі ➡️"
    PAGINATED_CHOICE_PAGE_LABEL = None  # hide page indicator
```

<details>
  <summary>(Click to see the result)</summary>
  <table>
    <tr>
      <td><img src="https://github.com/Romashkaa/telekit/blob/main/docs/images/paginated_choice.png?raw=true" alt="Example" width="300"></td>
    </tr>
  </table>
</details>

`choices` accepts a `dict[str, T]`, or any `Iterable[T]`.
If only one item is present, `on_choice` is called immediately without rendering a keyboard.

## Utils

| **Name**           | **Description**                                                    |
| ------------------ | ------------------------------------------------------------------ |
| `load_env`         | Load all key-value pairs from a `.env` file into a dictionary.     |
| `read_env_var`     | Read a single variable by name from a `.env` file.                 |
| `compose_keyboard` | Merge multiple button groups into a single inline keyboard with computed `row_width`. |

### Environment Utils

- `read_token` and `read_canvas_path` now support reading from `.env` files.
  Pass `".env"` to use the default key, or `".env:KEY"` to specify a custom one:

```python
read_token(".env")                 # reads TOKEN
read_token(".env:BOT_TOKEN")       # reads BOT_TOKEN

read_canvas_path(".env")           # reads CANVAS_PATH
read_canvas_path(".env:MY_CANVAS") # reads MY_CANVAS
```

### Inline Keyboard Utils

`compose_keyboard` combines multiple button groups into a single keyboard and automatically calculates `row_width` for each group.

Each group is laid out independently using its corresponding width from `widths`.
A width of `-1` means "all buttons in one row" (i.e. ``len(group)``).

| **Param** | **Type**         | **Description**                             |
|-----------|------------------|---------------------------------------------|
| `groups`  | `dict[str, Any]` | One or more button groups                   |
| `widths`  | `Iterable[int]`  | Row width per group or single value for all |

| **Returns** | **Type** |
|------------|----------|
| `keyboard` | `dict[str, Any]` |
| `row_width` | `tuple[int, ...]` |

```py
# row_width → (1, 3, 3, 3, 2)
# layout:
#   |    🆕 Create    |
#   |  1  |  2  |  3  |
#   |  4  |  5  |  6  |
#   |  7  |  8  |  9  |
#   | « Back | Next » |

keyboard, row_width = compose_keyboard(
    {"🆕 Create": "create"},
    {str(n): str(n) for n in range(1, 10)},
    {"« Back": "back", "Next »": "next"},
    widths=(-1, 3, -1), # or (1, 3, 2)
)
self.chain.set_inline_choice(keyboard, row_width)
```