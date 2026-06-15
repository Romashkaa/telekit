# Inline Keyboards

Inline keyboards let you attach interactive buttons directly to bot messages.
Depending on how much control you need, Telekit offers two approaches — a quick dict-based shorthand and a fluent builder with full layout control.

## Simple Inline Keyboards

The fastest way to add buttons to a message. Pass a plain `dict` where each key is the button label and each value is the callback to invoke when pressed.

<details>
<summary><code>chain.set_inline_keyboard()</code> <b>method</b></summary>

### `chain.set_inline_keyboard()` method

```python
self.chain.set_inline_keyboard(
    {
        "✏️ Change": self.change_name,
        "❌ Delete": self.delete,
    }
)
```

`row_width` controls how many buttons appear per row:

```python
self.chain.set_inline_keyboard(
    {
        "One":   self.one,
        "Two":   self.two,
        "Three": self.three,
        "Four":  self.four,
        "Five":  self.five,
    },
    row_width=(3, 2)  # first row: 3 buttons, second row: 2
)
```

```
╭──────────┬──────────┬──────────╮
│   One    │   Two    │  Three   │
├──────────┴──┬───────┴──────────┤
│    Four     │       Five       │
╰─────────────┴──────────────────╯
```

**Value types accepted:**

| **Value type**       | **Effect**                                 |
| -------------------- | ------------------------------------------ |
| `Callable`           | Called when the button is pressed.         |
| `str`                | Opens the URL in a browser.                |
| `InlineButton`       | Subclasses of this allow assigning any available button behaviour — covered in the [next page](./7_2_inline_buttons.md). |

</details>

> [!TIP]
> See [example](../examples/risk_game.md)

> [!CAUTION]
> Callbacks remain in memory until the user clicks a button or navigates away. To avoid indefinite waiting, see [Timeouts](9_timeouts.md).

## Builder Approach

When you need precise row layout or conditional buttons, use `InlineKeyboard` — a fluent builder that composes keyboards step by step.
It is more explicit, more readable, and handles complex layouts without counting `row_width` manually.

<details>
<summary><code>InlineKeyboard</code> <b>class</b></summary>

### `InlineKeyboard` class

```python
from telekit.types import InlineKeyboard
```

`InlineKeyboard` is built by chaining method calls. Call `.row()` to start a new row:

```python
InlineKeyboard()
    .add_callback("-", self.decrement, style="danger")
    .add_callback("+", self.increment, style="success")
.row()
    .add_callback("↺ Reset", self.reset)
```

```
╭──────────┬──────────╮
│    -     │    +     │
├──────────┴──────────┤
│       ↺ Reset       │
╰─────────────────────╯
```

**Layout helpers**

| **Method**     | **Description** |
| -------------- | --------------- |
| `row()`        | Finalize the current row and start a new one. |
| `column()`     | Every subsequent button gets its own row. Alias for `grid(1)`. |
| `column_end()` | Exit column mode and flush the current row. Alias for `grid_end()`. |
| `grid(width)`  | Every subsequent button is automatically split into rows of `width` buttons. `width=0` disables auto row breaks. |
| `grid_end()`   | Exit grid mode and flush the current row. |

**Button methods**

| **Method**            | **Description**                                                  |
| --------------------- | ---------------------------------------------------------------- |
| `add_callback(...)`   | Button that fires a callback function.                           |
| `add_link(...)`       | Button that opens a URL.                                         |
| `add_copy(...)`       | Button that copies text to the clipboard.                        |
| `add_alert(...)`      | Button that shows a popup alert dialog.                          |
| `add_notification(...)` | Button that shows a brief top-of-chat notification.            |
| `add_static(...)`     | Decorative button with no action.                                |
| `add_webapp(...)`     | Button that opens a Telegram Mini App.                           |
| `add_suggest(...)`    | Button that simulates the user sending a message.                |
| `add_invoke(...)`     | Button that calls a named method on an arbitrary object.         |
| `add(...)`            | Attach any raw `InlineButton` instance.                          |
| `extend(...)`         | Add multiple buttons from a `dict` or `list`.                    |
| `extend_rows(...)`    | Append one or more pre-built rows.                               |

All button methods accept a `style` parameter: `"danger"` (red), `"success"` (green), or `"primary"` (blue).

#### How to conditionally include the buttons?

The `when=` parameter on any method conditionally includes the button:

```python
InlineKeyboard()
    .add_callback("Edit", self.edit, when=self.user_is_admin)
    .add_callback("View", self.view)
```

</details>

<details>
<summary><code>chain.set_keyboard()</code> <b>method</b></summary>

### `chain.set_keyboard()` method


`set_keyboard()` is the universal method for attaching any keyboard to the current message. Pass it an `InlineKeyboard` instance:

```python
self.chain.set_keyboard(
    InlineKeyboard()
        .add_callback("-", self.decrement, style="danger")
        .add_callback("+", self.increment, style="success")
    .row()
        .add_callback("↺ Reset", self.reset)
)
self.chain.edit()
```
</details>

> [!TIP]
> See [example](../examples/counter.md)

> [!NOTE]
> `set_keyboard()` also accepts `ReplyKeyboard` — but reply keyboards are covered in a [later section](./7_3_reply_keyboard.md).


## Choice Keyboards

When every button leads to the same callback but with a different value — a product list, a color picker, a language selector — the choice API removes the boilerplate of wiring each button individually.

<details>
<summary><code>chain.set_inline_choice()</code> <b>method</b></summary>

### `chain.set_inline_choice()` method


Pass a callback and a `dict` of `{Label: Value}`. When the user taps a button, the value is passed directly to the callback:

```python
pages = {
    "💻 MacBook Pro": "Specs: M3 Chip, 16GB RAM, 512GB SSD. Price: $1999.",
    "📱 iPhone 17":   "Features: 48MP Camera. Price: $799.",
    "🎧 AirPods Max": "High-fidelity audio with ANC. Price: $549.",
}

self.chain.set_inline_choice(self.display_page, pages)
```

```python
def display_page(self, description: str) -> None:
    self.chain.sender.set_message(description)
    self.chain.edit()
```

`choices` accepts a `dict[str, T]` or any `Iterable[T]`.

</details>

> [!TIP]
> See full [example](../examples/logging.md).

> [!CAUTION]
> Values remain in memory until the user clicks or navigates away. See [Timeouts](9_timeouts.md).

## Suggested Replies

You can provide suggested replies for the user to tap instead of typing. Useful for guiding input with predefined options:

```python
self.chain.set_entry_suggestions(["Option A", "Option B", "Option C"])
```

## Want to go deeper?

- Inline Buttons
    - [Inline Button Types](./7_2_inline_buttons.md)
- Reply Keyboard
    - [Reply Keyboard](./7_3_reply_keyboard.md)
    - [Reply Keyboard Buttons](./7_4_reply_buttons.md)

[Next: Entries »](8_entries.md)