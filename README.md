![TeleKit](https://github.com/Romashkaa/images/blob/main/TeleKitWide.png?raw=true)

# TeleKit Library

**Telekit** is a declarative, developer-friendly library for building Telegram bots. It streamlines common bot operations, automates routine tasks, and provides a clear, structured way to implement complex logic without boilerplate.

Telekit comes with a built-in DSL for defining scenes, menus, FAQ pages, and multi-step flows, allowing developers to create fully interactive bots with minimal code. The library also handles message formatting, user input, and callback routing automatically, letting you focus on the bot’s behavior instead of repetitive tasks.

```python
self.chain.sender.set_text(Bold("Hello world!"))
self.chain.sender.set_photo("robot.png")
self.chain.set_inline_keyboard({"👋 Hello, Bot": self.handle_greeting})
self.chain.send()
```
> Example taken out of context

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

> Telekit DSL example

Even in its beta stage, Telekit accelerates bot development, offering ready-to-use building blocks for commands, user interactions, and navigation. Its declarative design makes bots easier to read, maintain, and extend.

**Key features:**  
- Declarative bot logic with **chains** for multi-step interactions  
- Built-in **DSL** for menus, buttons, and FAQ pages  
- Automatic handling of **message formatting** and **callback routing**  
- Ready-to-use FAQ system and navigation flows
- Minimal boilerplate, clean, and maintainable code  

[GitHub](https://github.com/Romashkaa/telekit)
[PyPi](https://pypi.org/project/telekit/)
[Telegram](https://t.me/+wu-dFrOBFIwyNzc0)
[Tutorial](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/0_tutorial.md)

## Contents

- [Overview](#overview)
    - [Message Formatting](#message-formatting)
    - [Text Styling](#text-styling-with-styles)
    - [Handling Callbacks](#handling-callbacks-and-logic)
- [Quick Guide](#quick-start)
- [Examples and Solutions](#examples-and-solutions)
    - [Counter](#counter)
    - [FAQ Pages (Telekit DSL)](#faq-pages-telekit-dsl)
    - [Registration](#registration)
    - [Dialogue](#dialogue)

## Overview

To get the most out of Telekit, we recommend following the full, [step-by-step tutorial](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/0_tutorial.md) that covers everything from installation to advanced features and DSL usage.

Even if you don’t go through the entire guide right now, you can quickly familiarize yourself with the core concepts, key building blocks, and basic workflows of Telekit below. This section will introduce you to chains, handlers, message formatting, and some examples, giving you a solid foundation to start building bots right away.

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
        self.chain.sender.set_title("⌨️ Enter your new name")
        self.chain.sender.set_message("Please type your new name below:")

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
self.chain.sender.set_use_italic(False)
self.chain.sender.set_use_newline(False)
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
        "« Change": prompt,  # Executes `prompt.send()` when clicked
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

For a full walkthrough, [check out our tutorial](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/0_tutorial.md)

---

# Examples and Solutions

If you're unsure how the examples work, [check out our tutorial](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/0_tutorial.md) for a full walkthrough.

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

For more details on the syntax, see the [Telekit DSL Syntax reference](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/11_telekit_dsl.md).  

For a complete, step-by-step walkthrough, [check out our full tutorial](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/0_tutorial.md).

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
        cls.on.command('entry').invoke(cls.handle)

        # Or define the handler manually:

        # @cls.on.command('entry')
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

If you're unsure how the examples work, [check out our tutorial](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/0_tutorial.md) for a full walkthrough.

## Developer 

Telegram: [Romashka](https://t.me/NotRomashka)

Gravatar: [Romashka](https://gravatar.com/notromashka)