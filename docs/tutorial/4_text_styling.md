# Text Styling in Telekit

Telekit provides a convenient `Styles` class for creating styled messages in **HTML** or **Markdown**.  
It allows you to:

- make text **Bold, Italic, Underlined, Strikethrough**, and more;
- combine multiple styles in a single string;
- **sanitize** user input to prevent breaking HTML/Markdown tags.

---

## 1. Don’t Convert Styles to Strings

You can freely combine different style objects in a single expression:

```python
Bold("Bold") + " and " + Italic("Italic")
```

When sending styled text, the sender automatically applies the correct **parse_mode** (`html` or `markdown`) for style objects:

```python
self.chain.sender.set_text(
    Underline(
        Bold("Bold"), " and ", Italic("Italic")
    )
)
self.chain.sender.set_parse_mode("html")  # applied to all styles 
self.chain.send()
```

If a style reaches the sender as a plain string, the sender can’t assign the correct parse_mode.
For example:

```python
self.chain.sender.set_text(
    f"{Bold("Bold")} and {Italic("Italic")}" # Може використатися різні parse_mode
)
```

Here the styles are already converted to text, so the sender no longer knows which formatting mode each part needs.

---

## 2. Import & Use Styles

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

---

## 3. Combining styles

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

---

## 4. Sanitizing text

- **set_text**: strings remain unchanged, HTML/Markdown tags are not modified.  
  To safely include user input, use `Sanitize(...)`.

```python
# If parse_mode=None, the text is not sanitized
# and will be displayed literally as "<b>Romashk</b>" in the chat
self.chain.sender.set_text("<b>Romashka</b>")       # "<b>Romashk</b>"
self.chain.sender.set_text("<b>Romashka<i></b>")    # "<b>Romashk<i></b>"

# The text will be displayed literally as "Romashka"
self.chain.sender.set_text(Bold("Romashka"))     # "Romashka"
self.chain.sender.set_text(Bold("Romashka<i>"))  # "Romashka<i>"

# HTML formatting enabled; text is not sanitized
# Any HTML tags will be interpreted by Telegram
self.chain.sender.set_parse_mode("html")
self.chain.sender.set_text("<b>Romashka</b>")    # Bold "Romashka"
self.chain.sender.set_text("<b>Romashka<i></b>") # Error code: 400.

# HTML formatting enabled; text is sanitized
self.chain.sender.set_parse_mode("html")
self.chain.sender.set_text(Bold("Romashka"))     # Bold "Romashka"
self.chain.sender.set_text(Bold("Romashka<i>"))  # Bold "Romashka<i>"

# Sanitized — HTML tags are escaped
self.chain.sender.set_text(Sanitize("<b>Romashka</b>")) # "<b>Romashka</b>"
```

- **set_title** and **set_message** behave similarly, BUT:
  1. If `parse_mode` was not set previously, they automatically set it to `"HTML"`.
  2. **set_title** automatically applies **Bold** to the text.
  3. **set_message** automatically applies **Italic** to the text.

```python
# HTML tags will be interpreted:
self.chain.sender.set_title("<i>Hello, user!</i>") # Bold + Italic "Hello, user!"
```

---

## 5. Example

```python
import telekit

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
        self.chain.sender.set_use_italics(False)
        self.chain.send()

telekit.Server("BOT_TOKEN").polling()
```

---

[Handler »](5_handler.md)