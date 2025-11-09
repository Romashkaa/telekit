![TeleKit](https://github.com/Romashkaa/images/blob/main/TeleKitWide.png?raw=true)

# TeleKit Library

**Telekit** is a compilation of my early unpublished libraries, now working together seamlessly as a single unit. Intuitive and flexible, it doesn’t restrict you—you can still use handlers and other elements from the original library. 

Instead, it adds new tools and a declarative style, where you only need to “fill in the fields” in `self.chain` and "confirm" using `self.chain.send()`. Telekit automatically formats messages, handles potential errors (like unclosed HTML tags), and processes user responses. 

[GitHub](https://github.com/Romashkaa/telekit)
[PyPi](https://pypi.org/project/telekit/)
[Telegram](https://t.me/TeleKitLib)
[Real Example](https://github.com/Romashkaa/Questly)

## Contents

- [Overview](#overview)
    - [Message Formatting](#message-formatting)
    - [Handling Callbacks](#handling-callbacks-and-logic)
- [Quick Guide](#quick-guide)
- [Chains](#chains)
    - [Case 1 — Using the Same Chain Across All Methods](#case-1--using-the-same-chain-across-all-methods)
    - [Case 2 — Using Separate Chains for Each Step](#case-2--using-separate-chains-for-each-step)
    - [Case 3 — Using Child Chains with Explicit Parent](#case-3--using-child-chains-with-explicit-parent)
    - [Case 4 — Using Sequential Child Chains](#case-4--using-sequential-child-chains)
- [Handler](#handler)
    - [User](#attribute-handleruser)
- [Listeners](#listeners)
- [Senders](#senders)
- [Chapters](#chapters)
- [Examples and Solutions](#examples-and-solutions)
    - [Counter](#counter)
    - [FAQ Bot](#faq-pages)
    - [Registration](#registration)
    - [Dialogue](#dialogue)

## Overview

The library is designed to reduce boilerplate code and make Python development more efficient:

```python
import telebot
import telekit

class NameHandler(telekit.Handler):

    @classmethod
    def init_handler(cls, bot: telebot.TeleBot) -> None:
        @cls.on_text("My name is {name}")
        def _(message: telebot.types.Message, name: str):
            cls(message).display_name(name)

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

bot = telebot.TeleBot("TOKEN")
telekit.Server(bot).polling()
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

## Quick Guide

Here is a `server.py` example (entry point) for a project on TeleKit

```python
import telebot
import telekit

import handlers # Package with all your handlers

bot = telebot.TeleBot("TOKEN")
telekit.Server(bot).polling()
```

Here you can see an example of the `handlers/__init__.py` file:

```python
from . import (
    start, entry, help
)
```

Here is an example of defining a handler using TeleKit (`handlers/start.py` file):

```python
import telekit
import typing

import telebot.types


class StartHandler(telekit.Handler):

    # ------------------------------------------
    # Initialization
    # ------------------------------------------

    @classmethod
    def init_handler(cls, bot: telebot.TeleBot) -> None:
        """
        Initializes the command handler.
        """
        @bot.message_handler(commands=['start']) # Standard handler declaration
        def handler(message: telebot.types.Message) -> None:
            cls(message).handle()

    # ------------------------------------------
    # Handling Logic
    # ------------------------------------------

    def handle(self) -> None:
	    # Get the `chain` object:
        chain: telekit.Chain = self.get_chain() 
        
        # Below we change the message view using `chain.sender`:
        chain.sender.set_title("Hello") # Set the title for the message
        chain.sender.set_message("Welcome to the bot! Click the button below to start interacting.") # Set the message text
        chain.sender.set_photo("https://static.wikia.nocookie.net/ssb-tourney/images/d/db/Bot_CG_Art.jpg/revision/latest?cb=20151224123450") # Add a photo to the message (optional)
        chain.sender.set_effect(chain.sender.Effect.PARTY) # Add an effect (optional)
		
		# Handler's own logic:
        def counter_factory() -> typing.Callable[[int], int]:
            count = 0
            def counter(value: int=1) -> int:
                nonlocal count
                count += value
                return count
            return counter
        
        click_counter = counter_factory()
		
		# Add a keyboard to the message via `chain`:
		#  {"⊕": 1, ...} - {"caption": value}
		#  The button caption should be a string
		#  The value of the button can be any object and is not sent to Telegram servers
        @chain.inline_keyboard({"⊕": 1, "⊖": -1}, row_width=2)
        def _(message: telebot.types.Message, value: int) -> None:
            #    ^                              ^
            # Callback turns to Message         |
            # Value from `{caption: value}` – not sent to Telegram servers

            chain.sender.set_message(f"You clicked {click_counter(value)} times") # Change the message text

            chain.edit_previous_message() # Сhange the previous message instead of sending the new one.
            # ^ You can also call this once at the beginning of the function: 
            # ^ `chain.set_always_edit_previous_message(True)`

            chain.send() # Edit previous message

        chain.send() # Send message
```

**It is recommended to declare each handler in a separate file and place all handlers in the handlers folder.** 

**But you can write everything in one file:**

```python
import telebot
import telekit

class NameAgeHandler(telekit.Handler):

    @classmethod
    def init_handler(cls, bot: telebot.TeleBot) -> None:
        """
        Initializes the message handlers.
        """
        @cls.on_text("My name is {name} and I am {age} years old")
        def _(message: telebot.types.Message, name: str, age: str):
            cls(message).handle(name, age)

        @cls.on_text("My name is {name}")
        def _(message: telebot.types.Message, name: str):
            cls(message).handle(name, None)

        @cls.on_text("I'm {age}  years old")
        def _(message: telebot.types.Message, age: str):
            cls(message).handle(None, age)

    def handle(self, name: str | None, age: str | None) -> None: 
        # Starting from TeleKit 0.0.3, the initial chain is created automatically.
        # However, you can still create a new one manually: `chain: telekit.Chain = self.get_chain()`

        if not name: 
            name = self.user.get_username()

        if not age:
            age = "An unknown number of"

        self.chain.sender.set_text(f"👋 Hello {name}! {age} years is a wonderful stage of life!")
        self.chain.send()

bot = telebot.TeleBot("TOKEN")
telekit.Server(bot).polling()
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
    def handle(self) -> None:
        self.chain.sender.set_text("1st page")
        self.chain.set_inline_keyboard(
            {
                "Next": self.handle_next
            }
        )
        self.chain.edit()

    def handle_next(self) -> None:
        self.chain.sender.set_text("2nd page")
        self.chain.set_inline_keyboard(
            {
                "Back": self.handle
            }
        )
        self.chain.edit()
```

Using the same `Chain` can help save memory and automatically replaces the previous message with smooth animations. However, it also retains previous settings. For example, if you don’t call `self.chain.set_inline_keyboard` in `handle_next` or otherwise (don't) update the inline keyboard, the old configuration will persist in the new message.

### Case 2 — Using Separate Chains for Each Step

In this approach, a new Chain instance is created for each step:

```python
class MyHandler(telekit.Handler):
    ...
    def handle(self) -> None:
        chain = self.get_chain()
        chain.sender.set_text("1st page")
        chain.set_inline_keyboard(
            {
                "Next": self.handle_next
            }
        )
        chain.edit()

    def handle_next(self) -> None:
        chain = self.get_chain()
        chain.sender.set_text("2nd page")
        chain.set_inline_keyboard(
            {
                "Back": self.handle
            }
        )
        chain.edit()
```

Using a separate Chain for each step is also fine for memory usage, but it won’t provide automatic animations—you’ll need to call `chain.sender.set_edit_message(...)` yourself. 

On the plus side, it doesn’t retain any previous settings.

### Case 3 — Using Child Chains with Explicit Parent

In this approach, each child chain is explicitly linked to a parent chain to avoid uncontrolled recursion:

```python
class MyHandler(telekit.Handler):
    ...
    def handle(self) -> None:
        main: telekit.Chain = self.get_chain()
        main.set_always_edit_previous_message(True)
        
        main.sender.set_title(...)
        main.sender.set_message(...)

        @main.inline_keyboard(pages)
        def _(message: telebot.types.Message, value: tuple[str, str]) -> None:
            page: telekit.Chain = self.get_child(main) # Explicitly assign `main` as the parent

            page.sender.set_title(value[0])
            page.sender.set_message(value[1])

            page.set_inline_keyboard({"« Back": main}) # btw: `page.parent` == `main`

            page.send()

        main.send()
```

If you don’t explicitly provide the parent chain, get_child will keep creating a child of the previous child indefinitely. The longer a user interacts with this function, the deeper the chain nesting grows, consuming more memory as each Chain object holds its inline keyboard and callbacks. Always specify the parent to prevent memory leaks.

### Case 4 — Using Sequential Child Chains

Each method creates a new child chain from the previous one, and (important:) there’s no way for the user to generate an infinite sequence:

```python
class MyHandler(telekit.Handler):
    ...
    def handle_1st(self) -> None:
        chain = self.get_chain()
        chain.sender.set_text("1st page")
        chain.set_inline_keyboard(
            {
                "Next": self.handle_2nd
            }
        )
        chain.edit()

    def handle_2nd(self) -> None:
        chain = self.get_child()
        chain.sender.set_text("2nd page")
        chain.set_inline_keyboard(
            {
                "Next": self.handle_3rd
            }
        )
        chain.edit()

    def handle_3rd(self) -> None:
        chain = self.get_child()
        chain.sender.set_text("3rd page")
        chain.edit()
```

Here everything is safe because there’s no “Back” button, so the user cannot endlessly create new chains that consume server memory. Each chain is a child of the previous one, but this sequence has a natural limit determined by program logic, preventing memory bloat.

### By the way:

- `self.get_chain()` and `self.get_child()` updates the `chain` attribute in the `handler` (`self.chain`):

```python
chain = self.get_chain()
print(chain == self.chain)   # True

child = self.get_child()
print(child == self.chain)   # True

print(chain == child)        # False
print(chain == child.parent) # True

# ---

chain1 = self.chain
self.get_chain()
print(chain1 == self.chain) # False
```

- Ways to create child chains:

```python
self.get_child()       # Child chain of previous chain
self.get_child(parent) # Or explicitly provide the parent chain

# Assign a parent chain after the current chain has been created:
self.get_chain().set_parent(parent)
```

### Other Chain`s Methods

#### Method `chain.edit_previous_message()`

Sets whether to edit the previously sent message instead of sending a new one.

```python
chain.edit_previous_message()  # The next chain.send() will edit the previous message
```

#### Method `chain.set_always_edit_previous_message()`

Allows you to specify that the previous message should always be edited when sending a new one.
When used in a chain, this setting is automatically applied to all (future) child chains of this object.

```python
chain.set_always_edit_previous_message(True)
```

---

#### Method `chain.get_previous_message()`

Returns the previously sent message (`telebot.types.Message`) or None if no message has been sent yet.

---

## Handler

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
        username = self.user.get_username()

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
        print(self.user.chat_id() == self.message.chat.id) # True
```

---


## Listeners

### Decorator `handler.on_text()`

Decorator for handling messages that match a given text pattern with placeholders {}. Each placeholder is passed as a separate argument to the decorated function:

```python
import telebot.types
import telekit

class OnTextHandler(telekit.Handler):

    @classmethod
    def init_handler(cls, bot: telebot.TeleBot) -> None:
        """
        Initializes the message handlers.
        """
        @cls.on_text("Name: {name}. Age: {age}")
        def _(message: telebot.types.Message, name: str, age: str):
            cls(message).handle(name, age)

        @cls.on_text("My name is {name} and I am {age} years old")
        def _(message: telebot.types.Message, name: str, age: str):
            cls(message).handle(name, age)

        @cls.on_text("My name is {name}")
        def _(message: telebot.types.Message, name: str):
            cls(message).handle(name, None)

        @cls.on_text("I'm {age}  years old")
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

### Decorator `handler.message_handler()`

Decorator for handling any kind of incoming message — text, photo, sticker, etc. The decorated function receives a `telebot.types.Message` object as a parameter. Handlers are executed in the order they are added.

```python
import telebot.types
import telekit
from typing import Callable, Any

class MessageHandlerExample(telekit.Handler):

    @classmethod
    def init_handler(cls, bot: telebot.TeleBot) -> None:
        """
        Initializes message handlers.
        """

        @cls.message_handler(commands=['help'])
        def help_handler(message: telebot.types.Message) -> None:
            cls(message).show_help()

        @cls.message_handler(regexp=r"^My name is (.+)$")
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

print(chapters["entry"])
# Output: "/entry — Example command for handling input"
```

This method allows you to separate content from code, making it easier to manage large texts or structured help documentation. It's especially useful for commands like `/help`, where each section can be displayed individually in a bot interface.

---

# Examples and Solutions

## Counter

```python
import telebot.types # type: ignore
import telekit
import typing


class Entry2Handler(telekit.Handler):

    # ------------------------------------------
    # Initialization
    # ------------------------------------------

    @classmethod
    def init_handler(cls, bot: telebot.TeleBot) -> None:
        """
        Initializes the message handler for the '/entry' command.
        """
        @bot.message_handler(commands=['entry2'])
        def handler(message: telebot.types.Message) -> None:
            cls(message).handle()

    # ------------------------------------------
    # Handling Logic
    # ------------------------------------------

    def handle(self) -> None:
        chain: telekit.Chain = self.get_chain()
         
        chain.sender.set_title("Hello")
        chain.sender.set_message("Welcome to the bot! Click the button below to start interacting.")

        def counter_factory() -> typing.Callable[[int], int]:
            count = 0
            def counter(value: int=1) -> int:
                nonlocal count
                count += value
                return count
            return counter
        
        click_counter = counter_factory()

        @chain.inline_keyboard({"⊕": 1, "⊖": -1}, row_width=2)
        def _(message: telebot.types.Message, value: int) -> None:
            chain.sender.set_message(f"You clicked {click_counter(value)} times") # The title remains unchanged (Hello)
            chain.edit() # Edit previous message

        chain.send()
```

## FAQ Pages

```python
import telebot.types
import telekit

pages: dict[str, tuple[str, str]] = {}

for title, text in telekit.chapters.read("help.txt").items():
    pages[title] = (title, text)

class HelpHandler(telekit.Handler):

    @classmethod
    def init_handler(cls, bot: telebot.TeleBot) -> None:
        """
        Initializes the command handler.
        """
        @bot.message_handler(commands=['help'])
        def handler(message: telebot.types.Message) -> None:
            cls(message).handle()

    # ------------------------------------------
    # Handling Logic
    # ------------------------------------------

    def handle(self) -> None:
        main: telekit.Chain = self.get_chain()
        main.set_always_edit_previous_message(True)
        
        main.sender.set_title("FAQ - Frequently Asked Questions")
        main.sender.set_message("Here are some common questions and answers to help you get started:")

        @main.inline_keyboard(pages)
        def _(message: telebot.types.Message, value: tuple[str, str]) -> None:
            page: telekit.Chain = self.get_child(main)

            page.sender.set_title(value[0])
            page.sender.set_message(value[1])

            page.set_inline_keyboard({"« Back": main})

            page.send()

        main.send()
```

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
    def init_handler(cls, bot: telebot.TeleBot) -> None:
        """
        Initializes the command handler.
        """
        @bot.message_handler(commands=['entry'])
        def handler(message: telebot.types.Message) -> None:
            cls(message).handle()

    # ------------------------------------------
    # Handling Logic
    # ------------------------------------------

    def handle(self) -> None:
        self._user_data = UserData(self.message.chat.id)
        self.entry_name()

    # -------------------------------
    # NAME HANDLING
    # -------------------------------

    # The message parameter is optional, 
    # but you can receive it to access specific information
    def entry_name(self, message: telebot.types.Message | None=None) -> None:
        self.chain.sender.set_title("⌨️ What`s your name?")
        self.chain.sender.set_message("Please, send a text message")

        self.add_name_listener()

        name: str | None = self._user_data.get_name( # from own data base
            default=self.user.get_username() # from telebot API
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
    def init_handler(cls, bot: telebot.TeleBot) -> None:
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

        self.chain.send() # Sends new message (it's dialogue)

    def handle_feeling(self, feeling: str):
        self.chain.sender.set_text(f"Got it, {self._user_name.title()}! You feel: {feeling}")
        self.chain.send()
```

## Developer 

Telegram: [Romashka](https://t.me/NotRomashka)

Gravatar: [Romashka](https://gravatar.com/notromashka)