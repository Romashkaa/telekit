# Inline Keyboards

In Telekit, inline keyboards enable interactive buttons directly within messages. There are two primary types:

1. **Label-Callback** Setter
2. **Label-Value** Decorator

## Label-Callback Keyboard

This type attaches buttons to a message, each linked to its own specific callback function.

Supported callback types include:  
- `Callable[[], Any]` – a function or method without parameters.  
- `Callable[[Message], Any]` – a function or method that receives the `Message` object.  
- `Chain` – triggers `.send()` on a chain.  
- `str` – opens a URL (not a callback in the traditional sense).

To add a Label-Callback keyboard, call `chain.set_inline_keyboard()` with a dictionary `{Label: Callback}`, optionally specifying `row_width`:

```python
self.chain.set_inline_keyboard(
    {
        "« Change": prompt,  # Executes `prompt()` when clicked
        "Yes »": lambda: print("User: Okay!"),  # Runs this lambda when clicked
        "Youtube": "https://youtube.com"  # Opens a link
    }, row_width=2
)
```

Explanation:  
- **Key** – text displayed on the button.  
- **Value** – callback executed when the button is pressed.  
- **row_width** – maximum number of buttons per row.

> [!CAUTION] 
> Callback functions remain in memory until the user clicks a button or navigates away. To forcibly terminate waiting, see [Timeouts](9_timeouts.md).

## Label-Value Keyboard

This type also attaches buttons to a message but uses a single shared callback for all buttons. Each button passes a unique (or non-unique) **value** to this callback.

The callback can accept any type.

To use the `inline_keyboard` decorator, provide a dictionary `{Label: Value}` and optionally `row_width`:

```python
@self.chain.inline_keyboard({
    "Red": (255, 0, 0),
    "Green": (0, 255, 0),
    "Blue": (0, 0, 255),
}, row_width=3)
def _(message, value: tuple[int, int, int]) -> None:
    r, g, b = value
    self.chain.set_text(f"You selected RGB color: ({r}, {g}, {b})")
    self.chain.edit()
```

Explanation:  
- **Key** – text displayed on the button.  
- **Value** – data passed to the callback when the button is clicked.  
- **row_width** – maximum number of buttons per row.

> [!CAUTION] 
> Values remain stored in memory until the user clicks a button or switches commands. To forcibly end waiting, see [Timeouts](10_timeouts.md).

## Row Width

`row_width` controls the number of buttons displayed per row in inline keyboards.

**Value types**:
- `int` - all rows will have the same number of buttons.
- `Iterable[int]` - allows specifying different numbers of buttons per row.
    - Each number in the iterable defines the number of buttons in the corresponding row.
    - If the total number of buttons exceeds the sum of the iterable, the remaining buttons are placed in additional rows using the last number in the iterable as the row width.

## Suggested Inline Options

You can provide suggested replies for the user to click instead of typing. This is useful for predefined input options.

```python
self.chain.set_entry_suggestions(["Suggestion 1", "Suggestion 2"])
```

## Example:

```python
import telekit

class NameHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        cls.on.text("My name is {name}").invoke(cls.display_name)

    def display_name(self, name: str) -> None:
        self.chain.sender.set_title(f"Hello {name}!")
        self.chain.sender.set_message("Your name has been set. You can change it below if you want")
        self.chain.set_inline_keyboard(
            {
                "✏️ Change": self.change_name
            }
        )
        self.chain.edit()

    def change_name(self):
        self.chain.sender.set_title("⌨️ Enter your new name")
        self.chain.sender.set_message("Oops, this feature will be available in the next section...")
        self.chain.edit()

telekit.Server("TOKEN").polling()
```

[Next: Entries »](8_entries.md)