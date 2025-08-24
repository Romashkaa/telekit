![TeleKit](https://github.com/Romashkaa/images/blob/main/TeleKitWide.png?raw=true)

# TeleKit Library

## Overview

**TeleKit** is a Python library designed to simplify common tasks for developers working with Telegram bots.  
It provides tools for:  

- Managing data with `Vault`, a lightweight interface for SQLite databases.  
- Organizing and processing text data using `chapters`, which allows converting `.txt` files into Python dictionaries for easy access.  
- Creating modular, reusable handlers and chains for structured code.  

The library is designed to reduce boilerplate code and make Python development more efficient.

[GitHub](https://github.com/Romashkaa/telekit)
[PyPi](https://pypi.org/project/telekit/)
[Telegram](https://t.me/TeleKitLib)

---

## Quick Guide

Here is a `server.py` example (entry point) for a project on TeleKit

```python

# Your server.py or main.py

import telebot
import telekit

import handlers # Package with all your handlers

bot = telebot.TeleBot("TOKEN")
telekit.Server(bot).polling()
```

Here is an example of defining a handler using TeleKit:

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

Here you can see an example of the `handlers/__init__.py` file:

```python
from . import start
from . import entry
from . import help
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

# Decorator `@chain.inline_keyboard()`

Allows you to add an inline keyboard to a message and process button presses:

```python
...

@chain.inline_keyboard({
    # Caption : Value
    # str     : Any
    "Red": (255, 0, 0),
    "Green": (0, 255, 0),
    "Blue": (0, 0, 255),
}, row_width=2) # Number of buttons in one line
def _(message: telebot.types.Message, value: tuple[int, int, int]) -> None:
    r, g, b = value
    chain.set_message(f"You selected RGB color: ({r}, {g}, {b})")
    chain.edit()  # Edit the previous message
```

Here:
- Adds an inline keyboard to the message with buttons for selecting a color.
- `value` can be any Python object (tuple, dict, class, etc.) and is not sent to Telegram servers.
- `chain.edit()` allows editing the previous message instead of sending a new one.
- The decorator makes interactive messages easy without manually handling callback data.

# Method `chain.set_inline_keyboard()`

This method allows you to add inline buttons to a message. 
Each button is bound to an action — either sending another chain, or executing a function/lambda. Buttons are placed in rows, and you can control how many buttons per row with the `row_width` parameter. 

```python
... # The full file is available in `telekit/example/example_handlers/entry.py`

chain.set_inline_keyboard(
    {
        "« Change": prompt, # When the user clicks this button, `prompt.send()` will be executed
        "Yes »": lambda message: print("User: Okay!")  # When the user clicks this button, this lambda function will run
    }, row_width=2
)
```

Here:
- Dictionary keys are the button labels.
- Values can be any callable (functions, methods, lambdas) or another Chain object, which will be executed via `.send()`.
- `row_width` defines how many buttons appear in a single row.

# Method `chain.set_entry_suggestions()`

Adds buttons with input suggestions to a message:
- Does not handle input by itself – you still need to use `@chain.entry()` or similar decorators.
- The user can still type their own value from the keyboard; these are just suggestions.

```python
chain.set_entry_suggestions(["Suggestion 1", "Suggestion 2"])
```

---

# Decorator `chain.entry()`

Allows handling user messages of any type (text, photo, stickers, etc.).

```python
... # The full file is available in `telekit/example/example_handlers/entry.py`

@chain.entry(
    filter_message=lambda message: True # Optional. Filters the user's message. If False, it will wait for the next response until the user's message passes the check and returns True.
    delete_user_response=True # Optional. If True, deletes every user message, even if it passes the check. If False, the user's messages will never be deleted.
)
def _(message: telebot.types.Message) -> None:
    # Handles the user's message here
    ...
```

# Decorator `chain.entry_text()`

Allows safe handling of text messages only from users.

```python
... # The full file is available in `telekit/example/example_handlers/entry.py`

@chain.entry_text(
    filter_message=lambda message, text: text.isdigit() # Optional. Filters the user's message. If False, it will wait for the next response until the user's message passes the check and returns True.
    delete_user_response=False # Optional. If True, deletes every user message, even if it passes the check. If False, the user's messages will never be deleted.
)
def _(message: telebot.types.Message, text: str) -> None:
    # Handles the user's message here
    number = int(text) # safe
    ...
```

---

# Method `handler.get_chain()`

Returns a new independent Chain object, which can be used to create your own message chains and inline keyboards.

```python
class HelpHandler(telekit.Handler):
    ...
    def handle(self) -> None:
        chain: telekit.Chain = self.get_chain()
        ...
```

# Method `handler.get_child()`

Returns a new Chain object that becomes a child chain of the current chain.
The child chain inherits settings from its parent but operates independently.

```python
class HelpHandler(telekit.Handler):
    ...
    def handle(self) -> None:
        chain: telekit.Chain = self.get_chain()
        ...
        child_chain: telekit.Chain = self.get_child() # Child chain of previous chain
        child_chain: telekit.Chain = self.get_child(chain) # Or explicitly provide the parent chain
        ...
```

You can directly create a child chain without specifying a parent:

```python
class HelpHandler(telekit.Handler):
    ...
    def handle(self) -> None:
        chain: telekit.Chain = self.get_child()
        ...
```

This approach is useful if the program works in a loop-like flow or needs to go back to previous steps.
Example: `telekit/example/example_handlers/entry.py`

---

# Attribute `handler.chain`

The methods `self.get_chain()` and `self.get_child()` automatically update `self.chain`, the current chain object the handler works with.

```python
class StartHandler(telekit.Handler):
    ...
    def handle(self) -> None:
        self.get_chain()

        self.chain.sender.set_text("OK!")

        self.chain.send()
```

# Attribute `handler.message`

```python
class StartHandler(telekit.Handler):
    ...
    def handle(self) -> None:
        self.message         # First message in the chain (probably the command that started it)
        self.message.chat.id # Chat ID
```

---

# Method `chain.edit_previous_message()`

Sets whether to edit the previously sent message instead of sending a new one.

```python
chain.edit_previous_message()  # The next chain.send() will edit the previous message
```

# Method `chain.set_always_edit_previous_message()`

Allows you to specify that the previous message should always be edited when sending a new one.
When used in a chain, this setting is automatically applied to all (future) child chains of this object.

```python
chain.set_always_edit_previous_message(True)
```

---

# Method `chain.send()`

Allows you to send a message or edit the previous one if `chain.edit_previous_message()` was called.

# Method `chain.edit()`

Automatically calls `chain.edit_previous_message()` to edit the last message.

```python
chain.edit_previous_message()
chain.send()

# OR

chain.edit() # – shorter!
```

---

# Method `chain.set_parent(parent: Chain)`

Allows you to assign a parent chain after the current chain has been created.

```python
chain.set_parent(other_chain)
```

---

# Method `chain.get_previous_message()`

Returns the previously sent message (`telebot.types.Message`) or None if no message has been sent yet.

---

# Object `handler.user`

The User class provides a simple abstraction for working with Telegram users inside your bot.
It stores the chat_id, the from_user object, and provides convenient methods to get the username.

**Method** `get_username() -> str | None`

Returns the username of the user.
- If the user has a Telegram username, it will be returned with an @ prefix.
- If not, falls back to the user’s first_name.
- If unable to fetch data, returns None.

```python
class StartHandler(telekit.Handler):
    ...
    def handle(self) -> None:
        username = self.user.get_username()

        if username:
            self.chain.sender.set_text(f"👋 Hello {username}!")
        else:
            self.chain.sender.set_text(f"🥴 Hello?")

        self.chain.send()
```

**Attribute** `chat_id: int`

```python
class StartHandler(telekit.Handler):
    ...
    def handle(self) -> None:
        self.user.chat_id() == self.message.chat.id # True
```

---

# Listeners

## Decorator `handler.on_text()`

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

---

# Senders

The Senders provide a convenient way to send, edit, and manage messages in Telegram bots.
They wrap the standard telebot API with extra functionality: temporary messages, automatic editing, error handling, and formatting helpers.

**BaseSender**

*Attributes*
- bot – global TeleBot instance.
- chat_id – chat ID to send messages to.
- text – message text.
- reply_markup – inline keyboard markup.
- is_temporary – whether the message is temporary.
- delele_temporaries – whether to delete previous temporary messages.
- parse_mode – formatting mode (HTML / Markdown).
- reply_to_message_id – ID of the message to reply to.
- edit_message_id – ID of the message to edit.
- thread_id – thread/topic ID. (????)
- message_effect_id – message effect (🔥, ❤️, …).
- photo – photo to send (URL or file_id).

*Public methods*
- set_text(text) – updates the message text.
- set_photo(photo) – sets the photo.
- set_chat_id(chat_id) – changes the chat.
- set_reply_markup(reply_markup) – adds inline/keyboard markup.
- set_temporary(is_temp) – marks the message as temporary.
- set_delete_temporaries(flag) – whether to delete previous temporary messages.
- set_parse_mode(mode) – sets formatting mode (html/markdown).
- set_reply_to(message) – sets the message to reply to.
- set_edit_message(message) – sets the message to edit.
- set_effect(effect) – sets the message effect (sender.Effect.PARTY or str).
- send() – sends or edits the message.
- send_or_handle_error() – sends the message; if an error occurs, sends the exception details.
- try_send() – attempts to send; returns (telebot.types.Message, exception).
- delete_message(message) – deletes a message.
- error(title, message) – sends a custom error message.
- pyerror(exception) – sends a Python exception message.
- get_message_id(message) – returns message_id.

**AlertSender**

Extends BaseSender and allows easy formatting of “alert” messages (**title** + *body*).

*Additional methods*
- set_title(title) – sets the alert title.
- set_message(*message, sep="") – sets the message body.
- set_use_italics(flag) – enable/disable italics for the message body.
- set_add_new_line(flag) – add/remove a blank line between title and message.
- send() – compiles text (title + message) and sends it.

---

# Chapters

TeleKit allows you to store large texts or structured information in `.txt` files and access them as Python dictionaries:

**`help.txt`**:

```txt
# intro
Welcome to TeleKit library. Here are the available commands:

# entry
/entry — Example command for handling input

# about
TeleKit is a general-purpose library for Python projects.
```

Usage in Python:

```python
import telekit

chapters: dict[str, str] = telekit.chapters.read("help.txt")

print(chapters["intro"])
# Output: "Welcome to TeleKit library. Here are the available commands:"

print(chapters["entry"])
# Output: "/entry — Example command for handling input"
```

This approach allows separating content from code and accessing text sections programmatically.

You can use this for the /help command (Below is an example)

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
            page: telekit.Chain = self.get_child()

            page.sender.set_title(value[0])
            page.sender.set_message(value[1])

            page.set_inline_keyboard({"« Back": main})

            page.send()

        main.send()
```

# Registration

```python
import telebot.types
import telekit

# Data Base

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
    
# /reg command handler

class RegHandler(telekit.Handler):

    @classmethod
    def init_handler(cls, bot: telebot.TeleBot) -> None:
        """
        Initializes the command handler.
        """
        @bot.message_handler(commands=['reg'])
        def handler(message: telebot.types.Message) -> None:
            cls(message).handle()

    # ------------------------------------------
    # Handling Logic
    # ------------------------------------------

    def handle(self) -> None:
        self._user_data = UserData(self.message.chat.id)
        self.input_name()

    def input_name(self, message: telebot.types.Message | None=None) -> None:
        prompt: telekit.Chain = self.get_child()
        prompt.set_always_edit_previous_message(True) # `chain.send()` will change the previous message instead of sending a new one
         
        prompt.sender.set_title("⌨️ What`s your name?")
        prompt.sender.set_message("Please, send a text message")

        name: str | None = self._user_data.get_name( # from own data base
            default=self.user.get_username() # from telebot API
        )
        
        if name:
            prompt.set_entry_suggestions([name])

        @prompt.entry_text(delete_user_response=True)
        def _(message: telebot.types.Message, name: str) -> None:
            confirm: telekit.Chain = self.get_child()

            confirm.sender.set_title(f"👋 Bonjour, {name}!")
            confirm.sender.set_message(f"Is that your name?")

            self._user_data.set_name(name)

            confirm.set_inline_keyboard(
                {
                    "« Change": prompt,
                    "Yes »": self.input_age,
                }, row_width=2
            )

            confirm.send() # Actually edits prompt message (REASON: prompt.set_always_edit_previous_message(True))

        prompt.send() # Sends new message

    def input_age(self, message: telebot.types.Message) -> None:
        prompt: telekit.Chain = self.get_child() # Child of `input_name.<locals>.confirm` (previous chain object)
         
        prompt.sender.set_title("⏳ How old are you?")
        prompt.sender.set_message("Please, send a numeric message")

        @prompt.entry_text(
            filter_message=lambda message, text: text.isdigit() and 0 < int(text) < 130,
            delete_user_response=True)
        def _(message: telebot.types.Message, text: str) -> None:
            confirm: telekit.Chain = self.get_child()

            confirm.sender.set_title(f"😏 {text} years old?")
            confirm.sender.set_message(f"Noted. Now I know which memes are safe to show you")
            self._user_data.set_age(int(text))

            confirm.set_inline_keyboard(
                {
                    "« Change": prompt,
                    "Ok »": self.result,
                }, row_width=2
            )

            confirm.send() # Actually edits prompt message

        prompt.send() # Actually edits previous message

    def result(self, message: telebot.types.Message) -> None:
        result: telekit.Chain = self.get_child() # Child of `input_age.<locals>.confirm` (previous chain object)
         
        result.sender.set_title("😏 Well well well")
        result.sender.set_message(f"So your name is {self._user_data.get_name()} and you're {self._user_data.get_age()}? Fancy!")

        result.set_inline_keyboard({"« Change": self.input_name})

        result.send() # Actually edits previous message
```

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

---

## Features

- Easy-to-use modular handlers and chains for structured project code.  
- `Vault` for persistent storage of Python data structures in SQLite.  
- `Chapters` for converting `.txt` files into Python dictionaries.  
- Lightweight and minimal dependencies, fully compatible with Python 3.12 and higher.

---

## Changelog 

Available in CHANGELOG.md

## Developer 

Telegram: [@TeleKitLib](https://t.me/TeleKitLib)