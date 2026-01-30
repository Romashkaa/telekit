# Text Styling

Telekit provides a convenient styles for creating styled messages in **HTML** or **Markdown**.  
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
    self.chain.sender.set_parse_mode("html")  # applied to all styles in message
    self.chain.send()
```

### The main rule

If a style reaches the sender as a plain string, the sender can’t assign the correct parse_mode:

```python
self.chain.sender.set_text(
    f"{Bold("Bold")} and {Italic("Italic")}"
)
```

Here, the styles are already converted to text, so there may be a mismatch between the sender and the intended style formatting, which is HTML by default.

## Import & Use Styles

Import `Styles` from `telekit.styles`:

```python
from telekit.styles import Styles

styles = Styles("markdown")
styles.bold("Bold") + styles.italic("Italic")
```

Or use individual styles:

```python
from telekit.styles import Bold, Italic

Bold("Bold") + Italic("Italic")
```

You can easily switch between HTML and Markdown without changing the code:

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
```

## Sanitizing Text

If `parse_mode=None`, and the text is not sanitized. Any HTML tags are displayed literally in the chat, for example `<b>Romashka</b>`. Tags will not be interpreted, and the raw text appears exactly as written.

```python
self.chain.sender.set_text("<b>Romashka</b>")       # "<b>Romashka</b>"
self.chain.sender.set_text("<b>Romashka<i></b>")    # "<b>Romashka<i></b>"
```

With `parse_mode=None`, using styles like `Bold()` will automatically sanitize the text inside them, so any HTML or special characters are safely escaped. The displayed text will be plain, with no interpreted tags.

```python
self.chain.sender.set_text(Bold("Romashka"))     # "Romashka"
self.chain.sender.set_text(Bold("Romashka<i>"))  # "Romashka<i>"
```

If `parse_mode="html"` and text is not sanitized, so any HTML tags in the string will be interpreted by Telegram. Unclosed or incorrect tags can produce errors.

```py
self.chain.sender.set_parse_mode("html")
self.chain.sender.set_text("<b>Romashka</b>")    # Bold "Romashka"
self.chain.sender.set_text("<b>Romashka<i></b>") # Error: unclosed "<i>" tag
```

When using `parse_mode="html"` together with styles (like `Bold()`), the text inside the style is automatically sanitized, ensuring that it won’t break the HTML formatting even if it contains special characters or tags

```py
self.chain.sender.set_parse_mode("html")
self.chain.sender.set_text(Bold("Romashka"))            # Bold "Romashka"
self.chain.sender.set_text(Bold("Romashka<i>"))         # Bold "Romashka<i>"
```

Using `Sanitize()` explicitly will escape all HTML and formatting tags inside the string, so the text is displayed literally in Telegram, regardless of the parse mode.

```py
self.chain.sender.set_parse_mode("html")
self.chain.sender.set_text(Sanitize("Romashka<i>"))     # "Romashka<i>"
self.chain.sender.set_text(Sanitize("<b>Romashka</b>")) # "<b>Romashka</b>"
```

## Example

```python
import telekit

from telekit.types import ParseMode
from telekit.styles import Group, Sanitize, Quote

class Start(telekit.Handler):
    @classmethod
    def init_handler(cls) -> None:
        cls.on.command("start").invoke(cls.start)

    def start(self):
        self.chain.sender.set_title(Group("Hello, ", Sanitize(self.user.first_name), "!"))
        self.chain.sender.set_message(
            "Quote of the Day:\n",
            Quote("The only way out is through."),
            "– Someone"
        )
        self.chain.sender.set_parse_mode(ParseMode.HTML)
        self.chain.send()

telekit.Server("BOT_TOKEN").polling()
```

[Next: Entries »](7_inline_keyboards.md)

// TODO: Explain all styles