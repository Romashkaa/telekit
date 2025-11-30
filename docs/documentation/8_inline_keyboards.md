# Inline Keyboards

This document describes all methods for creating and managing inline keyboards using Telekit.

---

## `set_inline_keyboard(keyboard: dict[str, 'Chain' | Callable[..., Any] | str], row_width: int = 1)`

Sets an inline keyboard for the chain, where each button triggers the corresponding action.

- **keyboard** – dictionary where keys are button labels and values are either:
  - `Callable[[], Any]` – function without parameters  
  - `Callable[[Message], Any]` – function with `Message` parameter  
  - `Chain` – triggers `.send()` on a chain  
  - `str` – URL to open when button is clicked  
- **row_width** – maximum number of buttons per row (default = 1)

**Example 1:**

```python
self.chain.set_inline_keyboard(
    {
        "« Change": prompt,  # Executes `prompt()` when clicked
        "Yes »": lambda: print("User: Okay!"),  # Runs this lambda when clicked
        "Youtube": "https://youtube.com"  # Opens a link
    }, row_width=2 # Buttons per line
)
```

**Example 2 (methods):**

```python
self.chain.set_inline_keyboard(
    {
        "« Change": self.change_name,
        "Next »": self.entry_age,
    }, row_width=2
)
```

---

## `inline_keyboard[Caption: str, Value](keyboard: dict[Caption, Value], row_width: int = 1) -> Callable`

Decorator to attach an inline keyboard to the chain. Each button passes its value to the decorated function.

- **keyboard** – dictionary mapping labels to values.  
- **row_width** – number of buttons per row (default = 1)

**Example:**

```python
@self.chain.inline_keyboard({
    "Red": (255, 0, 0),
    "Green": (0, 255, 0),
    "Blue": (0, 0, 255),
}, row_width=3)
def _(message, value: tuple[int, int, int]) -> None:
    r, g, b = value
    print(f"You selected RGB color: ({r}, {g}, {b})")
```

---

## `set_entry_suggestions(keyboard: dict[str, str] | list[str], row_width: int = 1)`

Sets reply suggestions below the message input as inline buttons.

- **keyboard** – list of strings or dictionary of `{Label: Value}` for quick replies  
- **row_width** – number of buttons per row (default = 1)

**Example:**

```python
self.chain.set_entry_suggestions(["Suggestion 1", "Suggestion 2"])
```

---

## Notes

- Callback functions remain in memory until clicked or the user navigates away.
- Use [Timeouts](10_timeouts.md) to forcibly terminate waiting callbacks.
- Inline keyboards support both individual button callbacks and shared callback functions via the decorator.

---

[Read more about Inline Keyboards](../tutorial/8_inline_keyboards.md)
[Handling User Input (Entries) »](9_entries.md)