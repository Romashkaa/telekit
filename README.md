![TeleKit](https://github.com/Romashkaa/images/blob/main/TeleKitWide.png?raw=true)

# TeleKit Library

**Telekit** is a declarative, developer-friendly library for building Telegram bots. It gives developers a dedicated Sender to manage message composition and a Chain to handle user input and responses.

```python
self.chain.sender.set_text(Bold("Hello world!"))
self.chain.sender.set_photo("robot.png")
self.chain.set_inline_keyboard({"👋 Hello, Bot": self.greet_user})
self.chain.send()
```
> Example taken out of context

Telekit comes with a [built-in DSL](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/11_telekit_dsl.md) for defining scenes, menus, FAQ pages, and multi-step flows, allowing developers to create fully interactive bots with minimal code. The library also handles message formatting, user input, and callback routing automatically, letting you focus on the bot’s behavior instead of repetitive tasks.

```js
@ main {
    title   = "🎉 Fun Facts Quiz";
    message = "Test your knowledge with 10 fun questions!";

    buttons {
        question_1("Start Quiz");
    }
}

@ question_1 {
    ...
}
```

> Basic Telekit DSL example

Even in its beta stage, Telekit accelerates bot development, offering ready-to-use building blocks for commands, user interactions, and navigation. Its declarative design makes bots easier to read, maintain, and extend.

**Key features:**  
- Declarative bot logic with **chains** for effortless handling of complex workflows
- [Ready-to-use DSL](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/11_telekit_dsl.md) for FAQs and other interactive scripts
- Automatic handling of [message formatting](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/4_text_styling.md) via [Sender](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/3_senders.md) and **callback routing**
- **Deep Linking** support with type-checked [Command Parameters](https://github.com/Romashkaa/telekit/blob/main/docs/examples/command_parameters.md) for flexible user input
- Built-in **Permission** and **Logging** system for user and event management  
- Seamless integration with [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI)
- Lightweight, maintainable, and easy-to-extend code

[GitHub](https://github.com/Romashkaa/telekit)
[PyPi](https://pypi.org/project/telekit/)
[Community](https://t.me/+wu-dFrOBFIwyNzc0)
[Tutorial](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/0_tutorial.md)

## Contents

- [Overview](https://github.com/Romashkaa/telekit/tree/main?tab=readme-ov-file#overview)
    - [Message Formatting](https://github.com/Romashkaa/telekit/tree/main?tab=readme-ov-file#message-formatting)
    - [Text Styling](https://github.com/Romashkaa/telekit/tree/main?tab=readme-ov-file#text-styling-with-styles)
    - [Handling Callbacks](https://github.com/Romashkaa/telekit/tree/main?tab=readme-ov-file#handling-callbacks-and-logic)
- [Quick Start](https://github.com/Romashkaa/telekit/tree/main?tab=readme-ov-file#quick-start)
- [Examples and Solutions](https://github.com/Romashkaa/telekit/blob/main/docs/examples/examples.md)
    - [Dialogue](https://github.com/Romashkaa/telekit/blob/main/docs/examples/dialogue.md)
    - [Risk Game](https://github.com/Romashkaa/telekit/blob/main/docs/examples/risk_game.md)
    - [Counter](https://github.com/Romashkaa/telekit/blob/main/docs/examples/counter.md)
    - [Quiz (Telekit DSL)](https://github.com/Romashkaa/telekit/blob/main/docs/examples/quiz.md)

## Overview

To get the most out of Telekit, we recommend following the full, [step-by-step tutorial](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/0_tutorial.md) that covers everything from installation to advanced features and DSL usage.

Even if you don’t go through the entire guide right now, you can quickly familiarize yourself with the core concepts of Telekit below. This section will introduce you to chains, handlers, message formatting, and some examples, giving you a solid foundation to start building bots right away.

Below is an example of a bot that responds to messages like "My name is {name}":

```python
import telekit

class NameHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        cls.on.text("My name is {name}").invoke(cls.display_name)

    def display_name(self, name: str) -> None:
        self.chain.sender.set_title(f"Hello {name}!")
        self.chain.sender.set_message("Your name has been set. You can change it below if you want")
        self.chain.set_inline_keyboard({"✏️ Change": self.change_name})
        self.chain.edit()

    def change_name(self):
        self.chain.sender.set_title("⌨️ Enter your name...")
        self.chain.sender.set_message("Please, type your new name below:")

        @self.chain.entry_text(delete_user_response=True)
        def name_handler(message, name: str):
            self.display_name(name)

        self.chain.edit()

telekit.Server("TOKEN").polling()
```

Let’s see how it works in practice 👇

## Message formatting:

- You can configure everything manually:

```python
self.chain.sender.set_text("*Hello, user!*\n\nWelcome to the Bot!")
self.chain.sender.set_parse_mode("markdown")
```
- Or let Telekit handle the layout for you:
```python
self.chain.sender.set_title("👋 Hello, user!") # Bold title
self.chain.sender.set_message("Welcome to the Bot!")  # Italic message after the title
```

Approximate result:

> **👋 Hello, user!**
> 
> _Welcome to the Bot!_

If you want more control, you can use the following methods:

```python
self.chain.sender.set_use_italics(False)
self.chain.sender.set_use_newline(False)
self.chain.sender.set_parse_mode("HTML")
self.chain.sender.set_reply_to(message)
self.chain.sender.set_chat_id(chat_id)

# And this is just the beginning...
```

Want to add an image, document or an effect in a single line?

```python
self.chain.sender.set_effect(self.chain.sender.Effect.HEART)
self.chain.sender.set_photo("url, bytes or path")
self.chain.sender.set_document("url, bytes or path")
self.chain.sender.set_text_as_document("Hello, this is a text document!")
```

Telekit decides whether to use `bot.send_message` or `bot.send_photo` automatically!

## Text Styling with `Styles`

Telekit provides a convenient style classes to create styled text objects for HTML or Markdown:

```python
Bold("Bold") + " and " + Italic("Italic")
```

Combine multiple styles:

```python
Strikethrough(Bold("Hello") + Italic("World!"))
```

Then pass it to set_text, `set_title`, or other sender methods, and the sender will automatically determine the correct `parse_mode`.

For more details, [see our tutorial](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/0_tutorial.md)

## Handling callbacks and Logic
If your focus is on logic and functionality, Telekit is the ideal library:

**Inline keyboard** with callback support:

```python
# Inline keyboard `label-callback`:
# - label:    `str`
# - callback: `Chain` | `str` | `func()` | `func(message)`
self.chain.set_inline_keyboard(
    {
        "« Change": prompt,  # Executes `prompt()` when clicked
        "Yes »": lambda: print("User: Okay!"),  # Runs this lambda when clicked
        "Youtube": "https://youtube.com"  # Opens a link
    }, row_width=2
)

# Inline keyboard `label-value`:
# - label: `str`
# - value: `Any`
@self.chain.inline_keyboard({
    "Red": (255, 0, 0),
    "Green": (0, 255, 0),
    "Blue": (0, 0, 255),
}, row_width=3)
def _(message, value: tuple[int, int, int]) -> None:
    r, g, b = value
    self.chain.set_message(f"You selected RGB color: ({r}, {g}, {b})")
    self.chain.edit()
```

**Receiving messages** with callback support:

```python
# Receive any message type:
@self.chain.entry(
    filter_message=lambda message: bool(message.text),
    delete_user_response=True
)
def handler(message):
    print(message.text)

# Receive text message:
@self.chain.entry_text()
def name_handler(message, name: str):
    print(name)

# Inline keyboard with suggested options:
chain.set_entry_suggestions(["Suggestion 1", "Suggestion 2"])

# Receive a .zip document:
@self.chain.entry_document(allowed_extensions=(".zip",))
def doc_handler(message: telebot.types.Message, document: telebot.types.Document):
    print(document.file_name, document)

# Receive a text document (Telekit auto-detects encoding):
@self.chain.entry_text_document(allowed_extensions=(".txt", ".js", ".py"))
def text_document_handler(message, text_document: telekit.types.TextDocument):
    print(
        text_document.text,      # "Example\n ..."
        text_document.file_name, # "example.txt"
        text_document.encoding,  # "utf-8"
        text_document.document   # <telebot.types.Document>
    )
```

Telekit is lightweight yet powerful, giving you a full set of built-in tools and solutions for building advanced Telegram bots effortlessly.

- You can find more information about the decorators by checking their doc-strings in Python.

---

## Quick Start

Telekit is published in [PyPI](https://pypi.org/project/telekit/), so it can be installed with one command:

```
pip install telekit
```

You can write the entire bot in a single file, but it’s recommended to organize your project using a simple structure like this one:

```
handlers/
    __init__.py
    start.py    # `/start` handler
    help.py     # `/help` handler
    ...
server.py       # entry point
```

Here is a `server.py` example (entry point) for a project on TeleKit

```python
import telekit
import handlers # Package with all your handlers

telekit.Server("BOT_TOKEN").polling()
```

Here you can see an example of the `handlers/__init__.py` file:

```python
from . import (
    start, help #, ...
)
```

Here is an example of defining a handler using TeleKit (`handlers/start.py` file):

```python
import telekit

class StartHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        ...
```

**One-file bot example (Echo Bot):**

```python
import telekit

class EchoHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        cls.on.text().invoke(cls.echo) # accepts all text messages

    def echo(self) -> None:
        self.chain.sender.set_text(f"{self.message.text}!")
        self.chain.send()

telekit.Server("TOKEN").polling()
```

For a full walkthrough, [check out our tutorial](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/0_tutorial.md) or see [Examples](https://github.com/Romashkaa/telekit/blob/main/docs/examples/examples.md)

---

## Developer 

Telegram: [Romashka](https://t.me/NotRomashka)

Gravatar: [Romashka](https://gravatar.com/notromashka)

[Community](https://t.me/+wu-dFrOBFIwyNzc0)