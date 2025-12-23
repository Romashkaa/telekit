# Text Styling in Telekit

This document lists all available style classes and their purpose.

---

## Styles

- `Bold` - makes text bold (`*text*` in Markdown, `<b>text</b>` in HTML)
- `Italic` - makes text italic (`_text_` in Markdown, `<i>text</i>` in HTML)
- `Underline` - underlines text (`__text__` in Markdown, `<u>text</u>` in HTML)
- `Strikethrough` - strikes through text (`~~text~~` in Markdown, `<s>text</s>` in HTML)
- `Code` - formats inline code (`` `text` `` in Markdown, `<code>text</code>` in HTML)
- `Python` - formats Python code blocks (``` ```python ... ``` ``` in Markdown, `<pre language="python">...</pre>` in HTML)
- `Spoiler` - hides text until clicked (`||text||` in Markdown, `<span class="tg-spoiler">text</span>` in HTML)
- `Quote` - formats text as a quote block (`text\n` in Markdown (nothing), and `<blockquote>text</blockquote>` in HTML)
- `Sanitize` - escapes HTML/Markdown tags to safely include user input
- `NoSanitize` - prevents escaping of HTML/Markdown tags
- `Link` - creates a clickable link (`[text](url)` in Markdown, `<a href="url">text</a>` in HTML)
- `UserLink` - creates a link to a user with an optional pre-filled (default) message
- `Styles.*`:
    - `Styles.bold(*content)` - creates a `Bold` object
    - `Styles.italic(*content)` - creates an `Italic` object
    - `Styles.underline(*content)` - creates an `Underline` object
    - `Styles.strike(*content)` - creates a `Strikethrough` object
    - `Styles.code(*content)` - creates a `Code` object
    - `Styles.python(*content)` - creates a `Python` code block object
    - `Styles.spoiler(*content)` - creates a `Spoiler` object
    - `Styles.quote(*content)` - creates a `Quote` object
    - `Styles.group(*content)` - creates a `Composite` object (combines multiple styles)
    - `Styles.sanitize(*content)` - creates a `Sanitize` object
    - `Styles.no_sanitize(*content)` - creates a `NoSanitize` object
    - `Styles.use_markdown()` - switches parse mode to Markdown
    - `Styles.use_html()` - switches parse mode to HTML
    - `Styles.set_parse_mode(parse_mode)` - manually sets parse mode (`"html"`, `"markdown"`, or `None`)

## Sanitizing

- **set_text**: strings remain unchanged, HTML/Markdown tags are not modified.  
  To safely include user input, use `Sanitize(...)`.

```python
# If parse_mode=None, the text is not sanitized
# and will be displayed literally as "<b>Romashka</b>" in the chat
self.chain.sender.set_text("<b>Romashka</b>")       # "<b>Romashka</b>"
self.chain.sender.set_text("<b>Romashka<i></b>")    # "<b>Romashka<i></b>"

# The text will be displayed literally, and with no tags
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

[Back to tutorial](../tutorial/4_text_styling.md)