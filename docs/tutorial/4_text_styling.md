# Text Styling in Telekit

Telekit provides a convenient `Styles` class for creating styled messages in **HTML** or **Markdown**.  
It allows you to:

- make text **bold, italic, underlined, strikethrough**, and more;
- combine multiple styles in a single string;
- **sanitize** user input to prevent breaking HTML/Markdown tags.

`Styles` can be used **through the sender** or **manually**.

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

You can easily switch between HTML and Markdown without changing the code:

```python
print(styles.bold("Text").markdown) # *Text*
print(styles.bold("Text").html)     # <b>Text</b>
print(styles.bold("Text").none)     # Text
```

---

## 2. Manual usage

Import all styles:

```python
from telekit.buildtext.styles import *
```

Using individual styles:

```python
Bold("Bold") + Italic("Italic")
```

Or through a `Styles` object:

```python
styles = Styles()
styles.bold("Text")    # creates bold text
styles.italic("Text")  # creates italic text
styles.group("Hello ", styles.bold("Romashka"), "!")  # combining
```

---

## 3. Combining styles

You can combine multiple styles:

```python
text = Strikethrough(Bold("Bold") + Italic("Italic"))
text = styles.strike(styles.bold("Bold") + styles.italic("Italic"))
```

- `+` joins text objects.
- The outer style applies to the entire result.

Grouping:

```python
styles.group("Hello ", styles.bold("Romashka"), "!")
```

---

## 4. Sanitizing text

- **set_text**: strings remain unchanged, HTML/Markdown tags are not modified.  
  To safely include user input, use `styles.sanitize(...)`.

```python
# Simple HTML, not sanitized
self.chain.sender.set_text("<b>Romashka</b>")

# HTML displayed as bold
self.chain.sender.set_parse_mode("html")
self.chain.sender.set_text("<b>Romashka</b>")

# Sanitized — HTML tags are escaped
styles = self.chain.sender.styles
self.chain.sender.set_text(styles.sanitize("<b>Romashka</b>"))  # &lt;b&gt;Romashka&lt;/b&gt;
```

- **set_title and set_message**: strings are **sanitized by default**:

```python
# HTML tags will be escaped
self.chain.sender.set_title("<i>Hello, user!</i>")

# Without sanitization (tags work)
styles = self.chain.sender.styles
self.chain.sender.set_title(styles.no_sanitize("<i>Hello, user!</i>"))
```

---

## 5. Example

```python
import telekit

class NameHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        cls.on.text().invoke(cls.greet)

    def greet(self):
        styles = self.chain.sender.styles
        self.chain.sender.set_text(
            styles.underline(
                "Hello, ", styles.bold("Dangerous username")
            )
        )
        self.chain.send()

telekit.Server("BOT_TOKEN").polling()
```

---

This structure ensures that beginners can safely use HTML or Markdown tags while giving full control over styling and text safety.

[Handler »](5_handler.md)