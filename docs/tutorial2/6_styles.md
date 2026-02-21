# Text Styling

Telekit provides a convenient styles for creating styled messages in **HTML** or **Markdown** (v2).  
It allows you to:

- make text **Bold, Italic, Underlined, Strikethrough**, and more;
- combine multiple styles in a single string;
- **Sanitize** user input to prevent breaking HTML/Markdown tags.

## Introduction

You can freely combine different style objects in a single expression:

```python
Bold("Bold") + " and " + Italic("Italic")
```

When sending styled text, the sender automatically applies the correct **parse_mode** (`html` or `markdown`) for style objects:

```python
def handle(self):
    self.chain.sender.set_text(
        Underline(
            Bold("Bold"), " and ", Italic("Italic")
        )
    )
    self.chain.sender.set_parse_mode("markdown")  # applied to all styles in message; HTML by deafault
    self.chain.send()
```

## Import & Use Styles

Import `Styles` namespace from `telekit.styles`:

```python
from telekit.styles import Styles

Styles.Bold("Bold") + Styles.Italic("Italic")
```

Or use individual styles:

```python
from telekit.styles import Bold, Italic, Raw

Bold("Bold") + Italic("Italic") + Raw("<u>Custom<u>")
```

You can easily switch between HTML and Markdown (v2) without changing the code:

```python
text = Bold("Bold") + " and " + Italic("Italic")

print(text.markdown) # *Bold* and _Italic_
print(text.html)     # <b>Bold</b> and <i>Italic</i>
print(text.none)     # Bold and Italic
```

- [See all Styles](../documentation/4_text_styling.md)

## Combining Styles

You can combine multiple styles:

```python
Strikethrough(Bold("Bold") + Italic("Italic"))
```

- `+` joins text objects.
- The outer style applies to the entire result.

Grouping:

```python
Group("Hello ", Bold("Romashka"), "!")
# Hello <b>Romashka</b>!
```

Separator `sep=`:

```python
Bold("Bold", Italic("Bold+Italic"), sep=", ").html
# <b>Bold, <i>Bold+Italic</i></b>
```

## Escaping

By default, **all plain strings are escaped** before sending. This prevents formatting tags from being interpreted — they will be displayed as literal text instead:

```python
self.chain.sender.set_text(
    "<b>Bold</b> and <i>Italic</i>"
)
# Result: "&lt;b&gt;Bold&lt;/b&gt; and &lt;i&gt;Italic&lt;/i&gt;"
```

If a style is converted to a string before being passed to the sender, it will be escaped and shown literally:
```python
self.chain.sender.set_text(
    f"{Bold('Bold').html} and {Italic('Italic').html}"
)
# Result: "&lt;b&gt;Bold&lt;/b&gt; and &lt;i&gt;Italic&lt;/i&gt;"
```

Instead, pass style objects directly — the sender handles rendering and escaping correctly:
```python
self.chain.sender.set_text(Bold("Bold"), " and ", Italic("Italic"))
# Result: "<b>Bold</b> and <i>Italic</i>"
```

To disable escaping, wrap the string in `Raw(...)` or pass `escape=False` to the style object or sender method:
```python
# Raw(...) — skip escaping for a pre-formatted string
pre_formatted: str = f"{Bold('Bold').html} and {Italic('Italic').html}"
self.chain.sender.set_text(Raw(pre_formatted))
# Result: "<b>Bold</b> and <i>Italic</i>"

# escape=False on the sender method
pre_formatted: str = f"{Bold('Bold').html} and {Italic('Italic').html}"
self.chain.sender.set_text(pre_formatted, escape=False)
# Result: "<b>Bold</b> and <i>Italic</i>"

# escape=False on the style object — useful for nested HTML/Markdown
self.chain.sender.set_text(Bold("<i>Hello!</i>", escape=False))
# Result: "<b><i>Hello!</i></b>

# escape=True on the style object
self.chain.sender.set_text(Bold("<i>Hello!</i>"))
# Result: "<b>&lt;i&gt;Hello!&lt;/i&gt;</b>
```

## Debugging

The style debugger renders a ``TextEntity`` tree and prints the result directly to the console — useful for previewing how your formatted text will look before sending it to Telegram.

Use the ``.debug()`` method on any style object and pass the desired parse mode:

```py

from telekit.styles import *

Group(
    Bold("🎵 Track List"),
    Stack(
        "Drugs",
        Group("R2, C1", "–", Bold("CDs"), sep=" "),
        "Hola",
        Group("Ashfal", "–", Italic("Divine"), sep=" "),
        start="  " + Stack.Markers.DOT,
        sep=";\n",
        end=".",
    ),
    Bold("Something next..."),
    sep="\n"
).debug("html")
```

<table> <tr>
    <td><img src="/docs/images/style_debugger.png" alt="Result" width="500"></td>
</tr> </table>

### 

```py
from telekit.styles import *
from telekit.senders import Sender

sender = Sender(472584)
sender.set_title("🎵 Track List")
sender.set_message(
    Stack(
        "Drugs",
        Group("R2, C1", "–", Bold("CDs"), sep=" "),
        "Hola",
        Group("Ashfal", "–", Italic("Divine"), sep=" "),
        start="  " + Stack.Markers.DOT,
        sep=";\n",
        end=".",
    ),
    Bold("Something next..."),
    sep="\n"
)
sender.set_use_newline(False)
sender.set_parse_mode("markdown")
sender.debug_text()
```

<table> <tr>
    <td><img src="/docs/images/sender_debugger.png" alt="Result" width="600"></td>
</tr> </table>

## Example

```python
import telekit
from telekit.styles import Group, Quote

class StartHandler(telekit.Handler):
    @classmethod
    def init_handler(cls) -> None:
        cls.on.command("start").invoke(cls.start)

    def start(self):
        self.chain.sender.set_title(f"Hello, {self.user.first_name}!")
        self.chain.sender.set_message(
            "Quote of the Day:\n",
            Quote("The only way out is through.", expandable=True),
            "– Someone"
        )
        self.chain.sender.debug_text()
        self.chain.send()

telekit.Server(BOT_TOKEN).polling()
```

[Next: Inline Keyboards »](7_inline_keyboards.md)