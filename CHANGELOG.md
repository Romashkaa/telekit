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
| `is_handoffed`      | `True` if this handler was reached via `handoff()`, `False` otherwise.           |
| `handoff_back()`    | Transfer control back to the origin handler.                                     |
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
| `paginated_choice(choices, on_choice, on_update, row_width)` | Display a paginated choice keyboard. |

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

| **Name**         | **Description**                                                    |
| ---------------- | ------------------------------------------------------------------ |
| `load_env`       | Load all key-value pairs from a `.env` file into a dictionary.     |
| `read_env_var`   | Read a single variable by name from a `.env` file.                 |

- `read_token` and `read_canvas_path` now support reading from `.env` files.
  Pass `".env"` to use the default key, or `".env:KEY"` to specify a custom one:

```python
read_token(".env")                 # reads TOKEN
read_token(".env:BOT_TOKEN")       # reads BOT_TOKEN

read_canvas_path(".env")           # reads CANVAS_PATH
read_canvas_path(".env:MY_CANVAS") # reads MY_CANVAS
```