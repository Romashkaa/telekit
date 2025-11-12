# Getting started

Telekit makes building Telegram bots fast and clean.  
Even if you’ve never written one before, this guide will take you from zero to a working bot in minutes.

### 1. Basic setup

First, get your bot token from [BotFather](https://t.me/BotFather), then create a simple server:

```python
import telekit

server = telekit.Server("BOT_TOKEN")
```

That’s it — your bot is connected.  
The `Server` handles all incoming messages and lets you start adding logic right away.

---

### 2. Creating a handler

Each piece of logic lives in its own handler — a class inherited from `telekit.Handler`.

```python
import telekit

class MyHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        # here we’ll define message triggers
        ...

telekit.Server("BOT_TOKEN").polling()  # start your bot
```

When the server starts, Telekit automatically finds all `Handler` subclasses and calls their `init_handler` methods. This is where you register triggers — points that tell the bot *when* to run your code.

Each handler stays isolated and simple — perfect for scaling your bot.

---

### 3. Using triggers

Let’s react to messages like “My name is Alice”:

```python
import telekit

class NameHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        cls.on.text("My name is {name}").invoke(cls.display_name)

    def display_name(self, name: str) -> None:
        self.chain.sender.set_title(f"👋 Hello {name}!")
        self.chain.sender.set_message("Welcome here!")
        self.chain.send()

telekit.Server("BOT_TOKEN").polling()
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

---

### 4. Echo-Bot

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

telekit.Server("BOT_TOKEN").polling()
```

Let’s take a closer look at the example. Here we’ve defined a handler that adds some logic. 

- The line `@cls.on.text().invoke(cls.echo)` is quite simple — it declares that `echo` should be ran every time a text message is received.

- `invoke` automatically creates a new instance of the `NameHandler` class for every incoming text message. After creating the instance, it passes the user’s `message` to it and calls the `echo` method.

- In 'echo', we compose the message (`self.chain.sender.set_text(f"{self.message.text}!")`) and send it (`self.chain.edit()`).

We’ll cover `self.chain` and `self.message` later, but for now, you can think of message as a regular telebot message object.

---

### 5. Developer tip

If you’re using an IDE like VS Code with **Pylance**, you’ll get autocompletion and type hints everywhere — Telekit is fully typed for your convenience :)

---

### 6. Run your bot

Finally, don’t forget to start polling:

```python
telekit.Server("BOT_TOKEN").polling()
```

Your bot is now live and ready to respond. 🎉

[Project structure »](2_project_structure.md)