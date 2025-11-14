## Handler - TEMP

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
