![TeleKit](https://github.com/Romashkaa/images/blob/main/TeleKitWide.png?raw=true)

[![PyPI](https://img.shields.io/pypi/v/telekit.svg)](https://pypi.org/project/telekit/)
[![Python](https://img.shields.io/pypi/pyversions/telekit.svg)](https://pypi.org/project/telekit/)

# Telekit Library

**Telekit** is a declarative, developer-friendly library for building Telegram bots. It gives developers a dedicated Sender to manage message composition and a Chain to handle user input and responses. The library also handles message formatting, user input, and callback routing automatically, letting you focus on the bot’s behavior instead of repetitive tasks.

```py
import telekit

class MyBotHandler(telekit.Handler):
    @classmethod
    def init_handler(cls):
        cls.on.command('start').invoke(cls.handle_start)

    def handle_start(self):
        self.chain.sender.set_text("Hello!")
        self.chain.sender.set_photo("robot.png")
        self.chain.send()

telekit.Server("BOT_TOKEN").polling()
```

> Example taken out of context

Telekit comes with a [built-in DSL](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/11_telekit_dsl.md), allowing developers to create fully interactive bots with minimal code. The DSL also supports **Jinja templates**, providing support for loops, conditionals, expressions, and filters directly within template fields to generate dynamic content.

```js
@ main {
    title   = "🎉 Fun Facts Quiz";
    message = "Test your knowledge with 10 fun questions!";

    buttons {
        question_1("Start Quiz");
    }
}
```

> See the [full example](https://github.com/Romashkaa/telekit/blob/main/docs/examples/quiz.md)

Even in its beta stage, Telekit accelerates bot development, offering ready-to-use building blocks for commands, user interactions, and navigation. Its declarative design makes bots easier to read, maintain, and extend.

**Key features:**  
- Declarative bot logic with **chains** for effortless handling of complex workflows
- [Ready-to-use DSL](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/11_telekit_dsl.md) for FAQs and other interactive scripts
- Automatic handling of [message formatting](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/4_text_styling.md) via [Sender](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/3_senders.md) and **callback routing**
- **Deep Linking** support with type-checked [Command Parameters](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/command_parameters.md) for flexible user input
- Built-in **Permission** and **Logging** system for user management
- Seamless integration with [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI)
- Fast to develop and easy-to-extend code

[GitHub](https://github.com/Romashkaa/telekit)
[PyPi](https://pypi.org/project/telekit/)
[Community](https://t.me/+wu-dFrOBFIwyNzc0)
[Gallery](https://github.com/Romashkaa/telekit/blob/main/docs/documentation/gallery.md)
[Examples](https://github.com/Romashkaa/telekit/blob/main/docs/examples/examples.md)
[Tutorial](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/0_tutorial.md)

## Contents

- [Overview](https://github.com/Romashkaa/telekit/tree/main?tab=readme-ov-file#overview)
    - [Message Formatting](https://github.com/Romashkaa/telekit/tree/main?tab=readme-ov-file#message-formatting)
    - [Text Styling](https://github.com/Romashkaa/telekit/tree/main?tab=readme-ov-file#text-styling-with-styles)
    - [Handling Callbacks](https://github.com/Romashkaa/telekit/tree/main?tab=readme-ov-file#handling-callbacks-and-logic)
    - [Command Parameters](https://github.com/Romashkaa/telekit/tree/main?tab=readme-ov-file#command-parameters-and-deep-linking)
- [Quick Start](https://github.com/Romashkaa/telekit/tree/main?tab=readme-ov-file#quick-start)
- [Examples and Solutions](https://github.com/Romashkaa/telekit/blob/main/docs/examples/examples.md)
    - [Dialogue](https://github.com/Romashkaa/telekit/blob/main/docs/examples/dialogue.md)
    - [Risk Game](https://github.com/Romashkaa/telekit/blob/main/docs/examples/risk_game.md)
    - [Counter](https://github.com/Romashkaa/telekit/blob/main/docs/examples/counter.md)
    - [Quiz (Telekit DSL)](https://github.com/Romashkaa/telekit/blob/main/docs/examples/quiz.md)

## Overview

> To get the most out of Telekit, we recommend following the full, [step-by-step tutorial](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/0_tutorial.md) that covers everything from installation to advanced features and DSL usage.

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
        def name_handler(name: str):
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
self.chain.sender.set_message("Welcome to the Bot!")  # Text after the title
```

Approximate result:

> **👋 Hello, user!**
> 
> Welcome to the Bot!

If you want more control, you can use the following methods:

```python
self.chain.sender.set_use_italics(True) # Italicize message body
self.chain.sender.set_use_newline(False) # Disable spacing between title and message
self.chain.sender.set_parse_mode(ParseMode.HTML) # Set parse mode. Use enum or string
self.chain.sender.set_reply_to(message)
self.chain.sender.set_chat_id(472584)
```

Want to add an image, document or an effect in a single line?

```python
self.chain.sender.set_effect(Effect.HEART) # Add effect to message. Use enum or string
self.chain.sender.set_photo("robot.png") # Attach photo. URL, file_id, or path
self.chain.sender.set_document("README.md") # Attach document. URL, file_id, or path
self.chain.sender.set_text_as_document("Hello, this is a text document!")
self.chain.sender.send_chat_action(ChatAction.TYPING) # Use enum or string
```

> [!NOTE]
> Telekit automatically decides whether to use `bot.send_message`, `bot.send_photo`, or other Telegram API methods.

More styling options are available in the [documentation](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/5_senders.md).

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

For more details, [see our tutorial](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/0_tutorial.md)

## Handling callbacks and Logic

If your focus is on logic and functionality, Telekit is the ideal library:

**Inline keyboard** with callback support:

> Inline keyboard `label-callback`:
```python
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

> Result:
```
╭────────────┬──────────┬──────────╮
│   Change   │   Okay   │  Reload  │
├────────────┴────┬─────┴──────────┤
│       PyPi      │     GitHub     │
├─────────────────┴────────────────┤
│            Copy Text             │
╰──────────────────────────────────╯
```

> Inline keyboard `label-value`:
```py
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

> Inline choice keyboard:
```py
self.chain.set_inline_choice(
    lambda value: print(f"User picked {value}"),
    choices=["Choice 1", "Choice 2"]
)
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
def name_handler(text: str):
    print(text)

# Inline keyboard with suggested options:
chain.set_entry_suggestions(["Suggestion 1", "Suggestion 2"])

# Receive a .zip document:
@self.chain.entry_document(allowed_extensions=(".zip",))
def doc_handler(document: telebot.types.Document):
    print(document.file_name, document)

# Receive a text document (Telekit auto-detects encoding):
@self.chain.entry_text_document(allowed_extensions=(".txt", ".js", ".py"))
def text_document_handler(text_document: telekit.types.TextDocument):
    print(
        text_document.text,      # "Example\n ..."
        text_document.file_name, # "example.txt"
        text_document.encoding,  # "utf-8"
        text_document.document   # <telebot.types.Document>
    )
```

Telekit is lightweight yet powerful, giving you a full set of built-in tools and solutions for building advanced Telegram bots effortlessly.

> [!TIP]
> You can find more information about the decorators by checking their doc-strings in Python.

## Command Parameters and Deep Linking

Telekit allows you to define **commands with typed parameters** and handle **deep links**. This makes it easy to pass arguments directly in the `/command parameter` call or through a URL link like `https://t.me/YourBot?start=parameter`.

You can define a command and specify expected parameter types using `telekit.parameters`:

```python
import telekit
from telekit.parameters import Int, Str

class StartHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        # Define parameters: first an integer, then a string
        cls.on.command("start", params=[Int(-1), Str()]).invoke(cls.handle)
    
    # Default values are required:   ↓↓↓↓                   ↓↓↓↓
    def handle(self, age: int | None=None, name: str | None=None):
        if age is None:
            self.chain.sender.set_text("Please provide your age and name.")
        elif age == -1:
            self.chain.sender.set_text("Invalid age provided.")
        elif name is None:
            self.chain.sender.set_text("Name is missing.")
        else:
            self.chain.sender.set_text(f"Hello {name}! You are {age} years old.")
        
        self.chain.send()
```

Send `/start 21 "Name Surname"` to your bot to see it in action.

---

## Quick Start

Telekit makes building Telegram bots fast and clean.  
Even if you’ve never written one before, this guide will take you from zero to a working bot in minutes.

### Installation

Telekit is published in [PyPI](https://pypi.org/project/telekit/), so it can be installed with command:

```
pip install telekit
```

### Getting a Bot Token

First, get your bot token from [BotFather](https://t.me/BotFather). 

After that, you can run the example bot to explore Telekit’s basic features:

```py
import telekit # import library

telekit.example(BOT_TOKEN) # run the example bot
```

### Basic Setup

To create your own bot server, replace `example` with the `Server` class and call `polling()` to start listening for updates:

```python
import telekit

telekit.Server(BOT_TOKEN).polling() # here
```

That’s it — your bot is connected.

### Eсho Bot Example

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

To understand how the example above works, I recommend continuing with:

[Creating Basic Handler »](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/2_basic_handler.md)

---

## Contact

- [Telegram](https://t.me/NotRomashka)
- [Gravatar](https://gravatar.com/notromashka)
- [Community](https://t.me/+wu-dFrOBFIwyNzc0)