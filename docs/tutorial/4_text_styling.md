# Text Styling in Telekit

Telekit provides a convenient `Styles` class for creating styled messages in **HTML** or **Markdown**.  
It allows you to:

- make text **bold, italic, underlined, strikethrough**, and more;
- combine multiple styles in a single string;
- **sanitize** user input to prevent breaking HTML/Markdown tags.

Styles can be used **through the sender** or **manually**.

---

## 1. Using via sender

The sender already has a `styles` object:

```python
styles = self.chain.sender.styles
text = styles.bold("Bold") + " and " + styles.italic("Italic")
```

When sending styled text, the sender automatically applies the correct **parse_mode** (`html` or `markdown`) for style objects:

```python
styles = self.chain.sender.styles
self.chain.sender.set_text(
    styles.underline(
        styles.bold("Bold"),
        " and ",
        styles.italic("Italic")
    )
)
self.chain.sender.set_parse_mode("html")
self.chain.send()
```

---

## 2. Manual usage

Import `Styles` from `telekit.styles`:

```python
from telekit.styles import Styles

styles = Styles()
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
styles.strike(styles.bold("Bold") + styles.italic("Italic"))
```

- `+` joins text objects.
- The outer style applies to the entire result.

Grouping:

```python
styles.group("Hello ", styles.bold("Romashka"), "!")
Group("Hello ", Bold("Romashka"), "!")
```

---

## 4. Sanitizing text

- **set_text**: strings remain unchanged, HTML/Markdown tags are not modified.  
  To safely include user input, use `styles.sanitize(...)`.

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

from telekit.styles import Sanitize, Underline

class NameHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        cls.on.text().invoke(cls.greet)

    def greet(self):
        self.chain.sender.set_text(
            Underline(
                "Hello, ", Sanitize("Dangerous <i>username")
            )
        )
        self.chain.sender.set_parse_mode("html")
        self.chain.send()

telekit.Server("BOT_TOKEN").polling()
```

---

This structure ensures that beginners can safely use HTML or Markdown tags while giving full control over styling and text safety.

[Handler »](5_handler.md)