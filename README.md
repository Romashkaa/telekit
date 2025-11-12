![TeleKit](https://github.com/Romashkaa/images/blob/main/TeleKitWide.png?raw=true)

# TeleKit Library

Telekit provides the easiest and most convenient way to work with the Telegram Bot API using a declarative interface, offering a wide range of built-in tools and ready-to-use solutions for fast bot development.

The library is currently in beta and doesn’t yet cover the entire Bot API, but it allows developers to seamlessly integrate telebot to fill in the current gaps. Despite being in early stages, Telekit significantly simplifies bot creation thanks to its clean, declarative design.

It automatically handles message formatting, user input, and potential errors (such as unclosed HTML tags), letting developers focus on building logic instead of boilerplate.

[GitHub](https://github.com/Romashkaa/telekit)
[PyPi](https://pypi.org/project/telekit/)
[Telegram](https://t.me/TeleKitLib)
[Tutorial](docs/tutorial/0_tutorial.md)

## Contents

- [Overview](#overview)
    - [Message Formatting](#message-formatting)
    - [Text Styling](#text-styling-with-styles)
    - [Handling Callbacks](#handling-callbacks-and-logic)
- [Quick Guide](#quick-start)
- [Chains](#chains)
    - [Case 1 — Using the Same Chain Across All Methods](#case-1--using-the-same-chain-across-all-methods)
    - [Case 2 — Using Separate Chains for Each Step](#case-2--using-separate-chains-for-each-step)
- [Handler](#handler)
    - [User](#attribute-handleruser)
- [Listeners](#listeners)
- [Senders](#senders)
- [Chapters](#chapters)
- [Examples and Solutions](#examples-and-solutions)
    - [Counter](#counter)
    - [FAQ Pages (Telekit DSL)](#faq-pages-telekit-dsl)
    - [Registration](#registration)
    - [Dialogue](#dialogue)

## Overview

Telekit focuses on reducing repetitive code and providing a clear, declarative way to define bot logic.
Instead of manually managing updates, states, or message parsing, you describe the behavior step by step using chains — the core concept that links handlers, messages, and user actions together.

Let’s see how it works in practice 👇

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
        self.chain.sender.set_title("⌨️ Enter your new name")
        self.chain.sender.set_message("Please type your new name below:")

        @self.chain.entry_text(delete_user_response=True)
        def name_handler(message, name: str):
            self.display_name(name)

        self.chain.edit()

telekit.Server("TOKEN").polling()
```

Let’s examine each element individually...

### Message formatting:

- You can configure everything manually:

```python
self.chain.sender.set_text("*Hello, user!*\n\nWelcome to the Bot!")
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

If you want more control:

```python
self.chain.sender.set_use_italic(False)
self.chain.sender.set_add_new_line(False)
self.chain.sender.set_parse_mode("HTML")
self.chain.sender.set_reply_to(message)
self.chain.sender.set_chat_id(chat_id)

# And this is just the beginning...
```

Want to add an image or an effect in a single line?

```python
self.chain.sender.set_effect(self.chain.sender.Effect.HEART)
self.chain.sender.set_photo("url, bytes or path")
```

Telekit decides whether to use `bot.send_message` or `bot.send_photo` automatically!

### Text Styling with `Styles`

Telekit provides a convenient `Styles` helper class to create styled text objects for HTML or Markdown. You can use it directly from your `self.chain.sender` or manually:

```python
...
# Automatically detects `parse_mode` from `sender`
styles = self.chain.sender.styles

text = styles.bold("Bold") + " and " + styles.italic("Italic")
...
```

Manual usage:

```python
# Manually create a Styles object
styles = Styles()
styles.use_html()                 # force HTML
styles.use_markdown()             # force Markdown
styles.set_parse_mode("markdown") # force Markdown
print(styles.bold("Text"))        # print as markdown

# Print directly
print(Bold("Text").markdown)
# or:
print(Bold("Text", parse_mode="markdown"))
```

Composition:

```python
# Combine multiple styles
text = Strikethrough(Bold("...") + Italic("..."))
text = styles.strike(styles.bold("...") + styles.italic())
```

### Handling callbacks and Logic
If your focus is on logic and functionality, Telekit is the ideal library:

- Inline keyboard:

```python
# Inline keyboard `label-callback`:
# - label:    `str`
# - callback: `Chain` | `str` | `Callable[[], Any]` | `Callable[[Message], Any]`
self.chain.set_inline_keyboard(
    {
        "« Change": prompt, # When the user clicks this button, `prompt.send()` will be executed
        "Yes »": lambda: print("User: Okay!"), # When the user clicks this button, this lambda function will run
        "Youtube": "https://youtube.com" # Can even be a link
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

- Receiving messages and files:

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

- You can find information about the new decorators by checking their doc-strings in Python.

---

## Quick Start

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
import telebot.types
import telekit
import typing


class StartHandler(telekit.Handler):

    # ------------------------------------------
    # Initialization
    # ------------------------------------------

    @classmethod
    def init_handler(cls) -> None:
        """
        Initializes the message handler for the '/start' command.
        """
        cls.on.message(['start']).invoke(cls.counter)

        # Or define the handler manually:

        # @cls.on.message(commands=['start'])
        # def handler(message: telebot.types.Message) -> None:
        #     cls(message).counter()

    # ------------------------------------------
    # Handling Logic
    # ------------------------------------------

    def counter(self) -> None:
        self.chain.sender.set_title("Hello!")
        self.chain.sender.set_message("Click the button below to start interacting")
        self.chain.sender.set_photo("https://static.wikia.nocookie.net/ssb-tourney/images/d/db/Bot_CG_Art.jpg/revision/latest?cb=20151224123450")
        self.chain.sender.set_effect(self.chain.sender.Effect.PARTY)

        def counter_factory() -> typing.Callable[[int], int]:
            count = 0
            def counter(value: int=1) -> int:
                nonlocal count
                count += value
                return count
            return counter
        
        click_counter = counter_factory()

        @self.chain.inline_keyboard({"⊕": 1, "⊖": -1}, row_width=2)
        def _(message: telebot.types.Message, value: int) -> None:
            self.chain.sender.set_message(f"You clicked {click_counter(value)} times")
            self.chain.edit()
        self.chain.set_remove_inline_keyboard(False)

        self.chain.send()
```

**One-file bot example:**

```python
import telekit

class NameAgeHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        @cls.on.text("My name is {name} and I am {age} years old")
        def _(message: telebot.types.Message, name: str, age: str):
            cls(message).handle(name, age)

        @cls.on.text("My name is {name}")
        def _(message: telebot.types.Message, name: str):
            cls(message).handle(name, None)

        @cls.on.text("I'm {age}  years old")
        def _(message: telebot.types.Message, age: str):
            cls(message).handle(None, age)

    def handle(self, name: str | None, age: str | None) -> None: 
        if not name: 
            name = self.user.username

        if not age:
            age = "An unknown number of"

        self.chain.sender.set_text(f"👋 Hello {name}! {age} years is a wonderful stage of life!")
        self.chain.send()

telekit.Server("TOKEN").polling()
```

---

## Chains

A `Chain` is the core element of Telekit, combining a `Sender` and an `InputHandler`.
(The latter usually works “under the hood,” so you typically don’t interact with it directly)

Proper usage of a Chain is crucial for predictable bot behavior.

### Case 1 — Using the Same Chain Across All Methods

In this approach, the same Chain instance is used throughout all methods of the class:

```python
class MyHandler(telekit.Handler):
    ...
    def first(self) -> None:
        self.chain.sender.set_text("1st page")
        self.chain.set_inline_keyboard(
            {
                "Next": self.second
            }
        )
        self.chain.edit()

    def second(self) -> None:
        self.chain.sender.set_text("2nd page")
        self.chain.set_inline_keyboard(
            {
                "Back": self.first
            }
        )
        self.chain.edit()
```

Using the same `Chain` can help save memory and automatically replaces the previous message with smooth animations. However, it also retains some previous settings.

### Case 2 — Using Separate Chains for Each Step

In this approach, a new Chain instance is created for each step:

```python
class MyHandler(telekit.Handler):
    ...
    def first(self) -> None:
        chain = self.get_local_chain()
        chain.sender.set_text("1st page")
        chain.set_inline_keyboard(
            {
                "Next": self.second
            }
        )
        chain.edit()

    def second(self) -> None:
        chain = self.get_local_chain()
        chain.sender.set_text("2nd page")
        chain.set_inline_keyboard(
            {
                "Back": self.first
            }
        )
        chain.edit()
```

Using a separate Chain for each step is also fine for memory usage, but it won’t provide automatic animations – you’ll need to call `chain.sender.set_edit_message(...)` yourself. 

On the plus side, it doesn’t retain any previous settings.

### By the way:

- `self.new_chain()` updates the `chain` attribute in the `handler` (`self.chain`):

```python
old = self.chain
self.new_chain()
print(old == self.chain)             # False (the "сhain" object has been replaced)

old2 = self.chain
local_chain = self.get_local_chain()
print(local_chain == self.chain)     # False ("local_chain" is local)
print(old2 == self.chain)            # True  (The "сhain" object remained)
```

---

## Handler

A `Handler` subclass defines how your bot reacts to messages or commands.  

- Each subclass should implement class method `init_handler(cls)` to register the message triggers (example: `cls.on.message(["start"]).invoke(cls.display_start)`).
- Instance methods like `handle()` or `display_name()` define the logic executed when a message matches a trigger.

> Essentially, you subclass `Handler`, register triggers in `init_handler`, and define responses in instance methods.


### Attribute `handler.message`

```python
class MyHandler(telekit.Handler):
    ...
    def handle(self) -> None:
        self.message         # First message in the chain (probably the user command / message that started it)
        self.message.chat.id # Chat ID
```

### User (`handler.user`)

The User class provides a simple abstraction for working with Telegram users inside your bot.
It stores the chat_id, the from_user object, and provides convenient methods to get the username.

#### User's Method `handler.user.get_username() -> str | None`

Returns the username of the user.
- If the user has a Telegram username, it will be returned with an @ prefix.
- If not, falls back to the user’s first_name.
- If unable to fetch data, returns None.

```python
class MyHandler(telekit.Handler):
    ...
    def handle(self) -> None:
        username = self.user.username

        if username:
            self.chain.sender.set_text(f"👋 Hello {username}!")
        else:
            self.chain.sender.set_text(f"🥴 Hello?")

        self.chain.send()
```

#### User's Method `handler.user.chat_id: int`

```python
class MyHandler(telekit.Handler):
    ...
    def handle(self) -> None:
        print(self.user.chat_id == self.message.chat.id) # True
```

---


## Listeners

### Decorator `handler.on.text()`

Decorator for handling messages that match a given text pattern with placeholders {}. Each placeholder is passed as a separate argument to the decorated function:

```python
import telebot.types
import telekit

class OnTextHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        """
        Initializes the message handlers.
        """
        @cls.on.text("Name: {name}. Age: {age}")
        def _(message: telebot.types.Message, name: str, age: str):
            cls(message).handle(name, age)

        @cls.on.text("My name is {name} and I am {age} years old")
        def _(message: telebot.types.Message, name: str, age: str):
            cls(message).handle(name, age)

        @cls.on.text("My name is {name}")
        def _(message: telebot.types.Message, name: str):
            cls(message).handle(name, None)

        @cls.on.text("I'm {age}  years old")
        def _(message: telebot.types.Message, age: str):
            cls(message).handle(None, age)

    # ------------------------------------------
    # Handling Logic
    # ------------------------------------------

    def handle(self, name: str | None, age: str | None) -> None: 

        if not name: 
            name = self.user.get_username()

        if not age:
            age = "An unknown number of"

        self.chain.sender.set_title(f"Hello {name}!")
        self.chain.sender.set_message(f"{age} years is a wonderful stage of life!")
        self.chain.send()
```

This allows you to define multiple on_text handlers with different patterns, each extracting the placeholders automatically.

### Decorator `handler.on.message()`

Decorator for handling any kind of incoming message — text, photo, sticker, etc. The decorated function receives a `telebot.types.Message` object as a parameter. Handlers are executed in the order they are added.

```python
import telebot.types
import telekit
from typing import Callable, Any

class MessageHandlerExample(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        """
        Initializes message handlers.
        """

        @cls.on.message(commands=['help'])
        def help_handler(message: telebot.types.Message) -> None:
            cls(message).show_help()

        @cls.on.message(regexp=r"^My name is (.+)$")
        def name_handler(message: telebot.types.Message) -> None:
            name = message.text.split("My name is ")[1]
            cls(message).greet(name)

    # ------------------------------------------
    # Handling Logic
    # ------------------------------------------

    def show_help(self) -> None:
        self.chain.sender.set_title("Help Menu")
        self.chain.sender.set_message("Here are some useful commands to get started...")
        self.chain.send()

    def greet(self, name: str) -> None:
        self.chain.sender.set_title(f"Hello {name}!")
        self.chain.sender.set_message("Welcome to the bot!")
        self.chain.send()
```

This allows you to define multiple message_handler decorators with different triggers (commands, regex patterns, content types, etc.) for flexible message processing. You can also use optional parameters such as whitelist to restrict handling to specific chat IDs.

---

## Senders

Senders in Telekit provide a high-level interface for sending and managing messages in Telegram bots. They wrap the standard TeleBot API, adding convenience features such as temporary messages, automatic editing, error handling, formatting, and effects.  

### Key Attributes:
- `bot`: The global TeleBot instance.
- `chat_id`: Target chat ID.
- `text`: Message text.
- `reply_markup`: Inline or keyboard markup.
- `is_temporary`: Marks the message as temporary.
- `delele_temporaries`: Deletes previous temporary messages if set.
- `parse_mode`: Message formatting (`HTML` or `Markdown`).
- `reply_to_message_id`: Optional message to reply to.
- `edit_message_id`: Optional message ID to edit.
- `thread_id`: Thread or topic ID (optional).
- `message_effect_id`: Optional effect like 🔥 or 🎉.
- `photo`: Optional photo to send.

### Key Methods:
- `set_text(text)`: Update the message text.
    - Or let Telekit handle the layout for you: 
    - `set_title(title)` + `set_message(message)`
    - `set_use_italics(flag)` – Enable/disable italics for the message body.
    - `set_add_new_line(flag)` – Add/remove a blank line between title and message.
- `set_photo(photo)`: Attach a photo.
- `set_parse_mode(mode)`: Set formatting mode.
- `set_reply_to(message)`: Reply to a specific message.
- `set_effect(effect)`: Apply a visual effect.
- `set_edit_message(message)`: Set the message to edit.
- `get_message_id(message)`: Get the ID of a message.
- `delete_message(message)`: Delete a message.
- `error(title, message)`: Send a custom error.
- `pyerror(exception)`: Send exception details.
- `send()`: Send or edit the message.
- `try_send()`: Attempt sending, returns `(message, exception)`.
- `send_or_handle_error()`: Send a message and show a Python exception if it fails.
- `set_temporary(flag)`: Mark message as temporary.
- `set_delete_temporaries(flag)`: Delete previous temporary messages.
- `set_chat_id(chat_id)`: Change target chat.
- `set_reply_markup(reply_markup)`: Add inline/keyboard markup. Raw.

---

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

---

# Examples and Solutions

## Counter

```python
import telebot.types
import telekit
import typing

class CounterHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        """
        Initializes the message handler for the '/counter' command.
        """
        @cls.on.message(['counter'])
        def handler(message: telebot.types.Message) -> None:
            cls(message).handle()

    def handle(self) -> None:
        self.chain.sender.set_title("Hello")
        self.chain.sender.set_message("Click the button below to start interacting")
        self.chain.sender.set_photo("https://static.wikia.nocookie.net/ssb-tourney/images/d/db/Bot_CG_Art.jpg/revision/latest?cb=20151224123450")
        self.chain.sender.set_effect(self.chain.sender.Effect.PARTY)

        def counter_factory() -> typing.Callable[[int], int]:
            count = 0
            def counter(value: int=1) -> int:
                nonlocal count
                count += value
                return count
            return counter
        
        click_counter = counter_factory()

        @self.chain.inline_keyboard({"⊕": 1, "⊖": -1}, row_width=2)
        def _(message: telebot.types.Message, value: int) -> None:
            self.chain.sender.set_message(f"You clicked {click_counter(value)} times")
            self.chain.edit()
        self.chain.set_remove_inline_keyboard(False)

        self.chain.send()
```

## FAQ Pages (Telekit DSL)

**Telekit DSL** — this is a custom domain-specific language (DSL) used to create interactive pages, such as FAQs.  
It allows you to describe the message layout, add images, and buttons for navigation between pages in a convenient, structured format that your bot can easily process.

The parser and analyzer provide an excellent system of warnings and errors with examples, so anyone can figure it out!

To integrate Telekit DSL into your project, simply add it as a Mixin to your Handler:

```python
import telekit

class GuideHandler(telekit.GuideMixin):
    @classmethod
    def init_handler(cls) -> None:
        cls.on.message(["faq"]).invoke(cls.start_script)
        cls.analyze_source(source)

source = """...Telekit DSL..."""

telekit.Server(TOKEN).polling()
```

- Even easier: call the appropriate method:

```python
import telekit

telekit.TelekitDSL.from_string("""...Telekit DSL...""", ["start"])

telekit.Server(TOKEN).polling()
```

```js
@ main {
    title   = "📖 FAQ - Frequently Asked Questions";
    message = "Here are some common examples to help you get started:";
    buttons {
        photo_demo("Image Example");    // Opens @photo_demo
        navigation("Navigation Demo");  // Opens @navigation
    }
}

@ photo_demo {
    title   = "🖼 Photo Example";
    message = "This page demonstrates how an image could be placed below this text.";
    image   = "https://static.wikia.nocookie.net/ssb-tourney/images/d/db/Bot_CG_Art.jpg/revision/latest?cb=20151224123450";
    buttons {
        back("⬅️ Back"); // "back" is magic variable (FILO stack)
    }
}

@ navigation {
    title   = "🧭 Navigation Demo";
    message = "This demonstrates multiple choices and auto-back handling.";

    // `buttons[2]` — Maximum 2 buttons per row (row_width=2)
    buttons[2] {
        option_a("A: Path One");
        option_b("B: Path Two");
        back("⬅️ Back");
    }
}

@ option_a {
    title   = "Path A";
    message = "You chose option A.";
    buttons {
        back("⬅️ Return");
    }
}

@ option_b {
    title   = "Path B";
    message = "You chose option B.";
    buttons {
        back("⬅️ Return");
    }
}
```

[Telekit DSL Syntax](docs/tutorial/11_telekit_dsl.md)

## Registration

```python
import telebot.types
import telekit

class UserData:
    names: telekit.Vault = telekit.Vault(
        path             = "data_base", 
        table_name       = "names", 
        key_field_name   = "user_id", 
        value_field_name = "name"
    )
    
    ages: telekit.Vault = telekit.Vault(
        path             = "data_base", 
        table_name       = "ages", 
        key_field_name   = "user_id", 
        value_field_name = "age"
    )
    
    def __init__(self, chat_id: int):
        self.chat_id = chat_id

    def get_name(self, default: str | None=None) -> str | None:
        return self.names.get(self.chat_id, default)

    def set_name(self, value: str):
        self.names[self.chat_id] = value

    def get_age(self, default: int | None=None) -> int | None:
        return self.ages.get(self.chat_id, default)

    def set_age(self, value: int):
        self.ages[self.chat_id] = value

class EntryHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        """
        Initializes the command handler.
        """
        cls.on.message(commands=['entry']).invoke(cls.handle)

        # Or define the handler manually:

        # @cls.on.message(commands=['entry'])
        # def handler(message: telebot.types.Message) -> None:
        #     cls(message).handle()

    # ------------------------------------------
    # Handling Logic
    # ------------------------------------------

    def handle(self) -> None:
        self._user_data = UserData(self.message.chat.id)
        self.entry_name()

    # -------------------------------
    # NAME HANDLING
    # -------------------------------

    def entry_name(self) -> None:
        self.chain.sender.set_title("⌨️ What`s your name?")
        self.chain.sender.set_message("Please, send a text message")

        self.add_name_listener()

        name: str | None = self._user_data.get_name( # from own data base
            default=self.user.username # from telebot API
        )
        
        if name:
            self.chain.set_entry_suggestions([name])

        self.chain.edit()

    def add_name_listener(self):
        @self.chain.entry_text(delete_user_response=True)
        def _(message: telebot.types.Message, name: str) -> None:
            self.chain.sender.set_title(f"👋 Bonjour, {name}!")
            self.chain.sender.set_message(f"Is that your name?")

            self._user_data.set_name(name)

            self.chain.set_inline_keyboard(
                {
                    "« Change": self.entry_name,
                    "Yes »": self.entry_age,
                }, row_width=2
            )

            self.chain.edit()

    # -------------------------------
    # AGE HANDLING
    # -------------------------------

    def entry_age(self, message: telebot.types.Message | None=None) -> None:
        self.chain.sender.set_title("⏳ How old are you?")
        self.chain.sender.set_message("Please, send a numeric message")

        self.add_age_listener()

        age: int | None = self._user_data.get_age()

        if age:
            self.chain.set_entry_suggestions([str(age)])

        self.chain.edit()

    def add_age_listener(self):
        @self.chain.entry_text(
            filter_message=lambda message, text: text.isdigit() and 0 < int(text) < 130,
            delete_user_response=True
        )
        def _(message: telebot.types.Message, text: str) -> None:
            self._user_data.set_age(int(text))

            self.chain.sender.set_title(f"😏 {text} years old?")
            self.chain.sender.set_message("Noted. Now I know which memes are safe to show you")

            self.chain.set_inline_keyboard(
                {
                    "« Change": self.entry_age,
                    "Ok »": self.show_result,
                }, row_width=2
            )
            self.chain.edit()

    # ------------------------------------------
    # RESULT
    # ------------------------------------------

    def show_result(self):
        name = self._user_data.get_name()
        age = self._user_data.get_age()

        self.chain.sender.set_title("😏 Well well well")
        self.chain.sender.set_message(f"So your name is {name} and you're {age}? Fancy!")

        self.chain.set_inline_keyboard({
            "« No, change": self.entry_name,
        }, row_width=2)

        self.chain.edit()
```

Optimized version: minimal memory usage and no recursive creation of chain objects

## Dialogue

```python
import telebot.types
import telekit
import typing

class DialogueHandler(telekit.Handler):

    # ------------------------------------------
    # Initialization
    # ------------------------------------------

    @classmethod
    def init_handler(cls) -> None:
        """
        Initializes message handlers
        """
        @cls.on_text("Hello!", "hello!", "Hello", "hello")
        def _(message: telebot.types.Message):
            cls(message).handle_hello()

    # ------------------------------------------
    # Handling Logic
    # ------------------------------------------

    def handle_hello(self) -> None:
        self.chain.sender.set_text("👋 Hello! What is your name?")

        @self.chain.entry_text()
        def _(message: telebot.types.Message, name: str):
            self.handle_name(name)
            
        self.chain.send()

    def handle_name(self, name: str):
        self._user_name: str = name

        self.chain.sender.set_text(f"Nice! How are you?")

        @self.chain.entry_text()
        def _(message, feeling: str):
            self.handle_feeling(feeling)

        self.chain.send()

    def handle_feeling(self, feeling: str):
        self.chain.sender.set_text(f"Got it, {self._user_name.title()}! You feel: {feeling}")
        self.chain.send()
```

## Developer 

Telegram: [Romashka](https://t.me/NotRomashka)

Gravatar: [Romashka](https://gravatar.com/notromashka)