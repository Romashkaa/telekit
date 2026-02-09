# Inline Keyboards

In Telekit, inline keyboards enable interactive buttons directly within messages: 

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
        self.chain.send()

    def change_name(self):
        self.chain.sender.set_title("⌨️ Enter your new name")
        self.chain.sender.set_message("Oops, this feature will be available in the next section...")
        self.chain.edit()

telekit.Server(BOT_TOKEN).polling()
```

Explanation:  
- The bot reacts to messages like `"My name is {name}"`.  
- It greets the user using the received name.  
- `self.chain.set_inline_keyboard` adds a "✏️ Change" button, which calls the `change_name` method when pressed.  
- In the `change_name` method, we update the message title and message body.  
- Using `self.chain.edit()`, we edit the previous bot message.  
- Next, we would allow the user to input text, but that will be covered in the following section.

There are two primary types of inline keyboards in Telekit:

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

```py
from telekit.types import LinkButton, CopyTextButton

self.chain.set_inline_keyboard(
    {   
        # When the user clicks this button, `change_name()` will be executed
        "Change": change_name,
        # When the user clicks this button, this lambda function will run
        "Okay": lambda: print("User: Okay!"),
        # When the user clicks this button, this method will be executed
        "Reload": self.reload,
        # Can even be a link (`str` or `LinkButton` object)
        "PyPi": "https://pypi.org/project/telekit/",
        "GitHub": LinkButton("https://github.com/Romashkaa/telekit"),
        # Or copy button
        "Copy Text": CopyTextButton("Text to copy")
    }, row_width=(3, 2, 1)
)
```
- Result
```
╭────────────┬──────────┬──────────╮
│   Change   │   Okay   │  Reload  │
├────────────┴────┬─────┴──────────┤
│       PyPi      │     GitHub     │
├─────────────────┴────────────────┤
│            Copy Text             │
╰──────────────────────────────────╯
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
def _(value: tuple[int, int, int]) -> None:
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

## Other Keyboards

While `(set_)inline_keyboard` focuses on **mapping actions** (calling different functions or passing static data), the `(set_)inline_choice` methods are specialized for **selecting from a set of options**.

- `set_inline_choice` – A method that takes an existing function and a collection of options. Ideal when your processing logic is already defined elsewhere – this is the most "Telekit-style" way to build selection menus.
- `inline_choice` – A decorator that turns the following function into a handler for the selected value. 

```py
pages = {
    "💻 MacBook Pro": "Specs: M3 Chip, 16GB RAM, 512GB SSD. Price: $1999.",
    "📱 iPhone 17": "Features: 48MP Camera. Price: $799.",
    "🎧 AirPods Max": "High-fidelity audio with Active Noise Cancellation. Price: $549."
}
self.chain.set_inline_choice(self.display_page, pages)
```

> [!TIP]
> See full [example](../examples/logging.md)

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

[Next: Entries »](8_entries.md)