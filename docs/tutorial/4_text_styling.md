# Text Styling

Telekit provides a convenient `Styles` helper class to create styled text objects for HTML or Markdown. You can use it directly from your `self.chain.sender` or manually.

## Automatic usage via sender

```python
...
# Automatically detects `parse_mode` from `sender`
styles = self.chain.sender.styles

text = styles.bold("Bold") + " and " + styles.italic("Italic")
print(text)          # <b>Bold</b> and <i>Italic</i> (auto)
print(text.html)     # <b>Bold</b> and <i>Italic</i> (force HTML)
print(text.markdown) # *Bold* and _Italic_           (force Markdown)
```

Then pass it to the sender:

```python
class MyHandler(telekit.Handler):
    ...
    def greet(self):
        styles = self.chain.sender.styles
        text = styles.underline(styles.bold("Bold"), " and ", styles.italic("Italic"))
        self.chain.sender.set_text(text)
        self.send()
```

`styles.bold()`, `styles.italic()`, and `styles.underline()` apply text formatting. They can be combined for more complex formatting.

## Manual usage:

1. Import all types

```python
from telekit.buildtext.styles import *
```

2.1. Use styles individually:

```python
Bold("III") + Italic("///")
```

2.2. (or) Use via a single Styles object:

```python
styles = Styles()
styles.use_html()                 # force HTML
styles.use_markdown()             # force Markdown
styles.set_parse_mode("markdown") # force Markdown ↰
print(styles.bold("Text"))        # print as markdown
```

Styles() allows switching between HTML and Markdown easily without changing code.

3. The same:

```python
print(Bold("Text").markdown)
print(Bold("Text", parse_mode="markdown"))
```

## Combining styles:

Combine multiple styles

```python
text = Strikethrough(Bold("...") + Italic("..."))
text = styles.strike(styles.bold("...") + styles.italic())
```

"+" joins text objects, and the outer style (Strikethrough) applies to the whole result.

---

## Example

```python
import telekit

class NameHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        cls.on.text().invoke(cls.greet) # accepts all text messages

    def greet(self):
        styles = self.chain.sender.styles
        text = styles.underline(styles.bold("Bold"), " and ", styles.italic("Italic"))
        self.chain.sender.set_text(text)
        self.chain.send()

telekit.Server("BOT_TOKEN").polling()
```


