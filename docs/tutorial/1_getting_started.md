# Getting started

> [!CAUTION]
> This documentation covers an outdated version of the library. Some information may no longer be accurate. Please refer to the [latest version of the tutorial](../tutorial2/0_tutorial.md).

Telekit makes building Telegram bots fast and clean.  
Even if you’ve never written one before, this guide will take you from zero to a working bot in minutes.

## Installation

Telekit is published in [PyPI](https://pypi.org/project/telekit/), so it can be installed with command:

```
pip install telekit
```

## 1. Basic setup

First, get your bot token from [BotFather](https://t.me/BotFather), then create a simple server:

```python
import telekit

server = telekit.Server(BOT_TOKEN)
```

That’s it — your bot is connected.  
The `Server` handles all incoming messages and lets you start adding logic right away.

You can also run the example bot to see the basic features in action:

```py
import telekit

telekit.example(BOT_TOKEN) # run the example bot
```

## 2. Basic concepts and Logic

- **Update** — a new message sent by the user that initiates the processing chain in Telekit. Such messages are catched by triggers (`Handler.on`). If a message was sent as a response to `chain.entry_text`, it is intercepted and processed by the chain itself, without involving triggers.
- **Handler** — a class that inherits from `telekit.Handler`, where you define the logic for processing updates from the server (for example, the `/start` command).
- **Triggers** (`YourHandler.on.*`) — each handler has an `on` object that provides trigger methods such as `text`, `command`, and others. These triggers listen for incoming updates from the server and initiate processing. Each handler may define multiple triggers.
- **Chain** (`your_handler.chain`) — each handler instance has a `chain` object responsible for linking message sending with handling the user’s response (for example, pressing an inline button or sending a message).
- **Sender** (`your_handler.chain.sender`) — each `chain` has a `sender` object that defines the appearance of the message: text, photos, effects, and more.

When an update arrives from the server, for example the `/start` command, the corresponding trigger receives it, creates an instance of its handler (at this point, `chain` and `sender` are created as well), and initiates the processing chain by calling a method where you implement the handling logic: configuring the bot’s response appearance using `self.chain.sender.*`, adding user response handling via `self.chain.set_inline_keyboard(...)` (or other methods), and finally sending the message using `self.chain.send()`.

## 3. Creating a handler

Each piece of logic lives in its own handler – a class inherited from `telekit.Handler`.

```python
import telekit

class MyHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        # here we’ll define message triggers
        ...

telekit.Server(BOT_TOKEN).polling()  # start your bot
```

When the server starts, Telekit automatically finds all `Handler` subclasses and calls their `init_handler` methods. This is where you register triggers — points that tell the bot *when* to initiate the processing chain.

Each handler stays isolated and simple — perfect for scaling your bot.

## 4. Using triggers

Let’s react to messages like "My name is Alice":

```python
import telekit

class NameHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        # when a message matches "My name is {name}", call "display_name" method:
        cls.on.text("My name is {name}").invoke(cls.display_name)

    def display_name(self, name: str) -> None:
        self.chain.sender.set_text(f"👋 Hello {name}!") # set text
        self.chain.send()                               # send
 
telekit.Server(BOT_TOKEN).polling()
```

Here, `cls.on.text("My name is {name}")` listens for that pattern.  
When triggered, the bot calls `display_name()` with the extracted variable `name`.

Triggers like `cls.on.text()` can be used in two ways — as a method or as a decorator:

```python
# method:
cls.on.text("My name is {name}").invoke(cls.display_name)

# decorator:
@cls.on.text("My name is {name}")
def _(message: telebot.types.Message, name: str):
    cls(message).display_name(name)
```

The decorator version gives you full access to the raw message and its arguments, but you’ll need to manually create the handler instance (`cls(message)`).

## 5. Example: Echo-Bot

Let’s make the bot a bit more simpler:

```python
import telekit

class EchoHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        cls.on.text().invoke(cls.echo) # accepts all text messages

    def echo(self) -> None:
        self.chain.sender.set_text(f"{self.message.text}!")
        self.chain.send()

telekit.Server(BOT_TOKEN).polling()
```

Let’s take a closer look at the example. Here we’ve defined a handler that adds some logic:

- The line `@cls.on.text().invoke(cls.echo)` is quite simple — it declares that `echo` should be ran every time a text message is received.

- `invoke` automatically creates a new instance of the `NameHandler` class for every incoming text message. After creating the instance, it passes the user’s `message` to it and calls the `echo` method.

- In 'echo', we compose the message (`self.chain.sender.set_text(f"{self.message.text}!")`) and send it (`self.chain.edit()`).

- `self.message` is the message object received by the trigger that initiated the processing.

## 6. Run your bot

Finally, don’t forget to start polling:

```python
telekit.Server(BOT_TOKEN).polling()
```

Your bot is now live and ready to respond. 🎉

> [!NOTE]
> If you’re using an IDE like VS Code with **Pylance**, you’ll get type hints everywhere — Telekit is fully typed for your convenience :)

[Next: Project structure »](2_project_structure.md)