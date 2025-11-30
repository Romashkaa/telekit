## Chapters

TeleKit provides a simple way to organize large texts or structured content in `.txt` files and access them as Python dictionaries. This is ideal for help texts, documentation, or any content that should be separate from your code.

### How It Works

Each section in a `.txt` file starts with a line beginning with `#`, followed by the section title. All subsequent lines until the next `#` are treated as the content for that section.

### Example `help.txt`

```
# intro
Welcome to TeleKit library. Here are the available commands:

# commands
/start — Start command
/entry — Example command for handling input

# about
TeleKit is a general-purpose library for Python projects.
```

You can parse this file in Python:

```python
import telekit

chapters: dict[str, str] = telekit.chapters.read("help.txt")

print(chapters["intro"])
# Output: "Welcome to TeleKit library. Here are the available commands:"

print(chapters["commands"])
# Output: "/start — Start command\n/entry — Example command for handling input"
```

This method allows you to separate content from code, making it easier to manage large texts or structured help documentation. It's especially useful for commands like `/help`, where each section can be displayed individually in a bot interface.
