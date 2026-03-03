# Project structure

> [!CAUTION]
> This documentation covers an outdated version of the library. Some information may no longer be accurate. Please refer to the [latest version of the tutorial](../tutorial2/0_tutorial.md).

You can write your bot in a single file or organize it.

## Multi-file bot Example

It’s recommended to organize your project using a simple structure like this one:

```
handlers/
    __init__.py
    start.py    # `/start` handler
    help.py     # `/help` handler
server.py       # entry point
```

Entry point, `server.py`:

```python
import telekit
import handlers  # Your handlers package

telekit.Server("BOT_TOKEN").polling()
```

Packages, `handlers/__init__.py`:

```python
from . import (
    start, help
)
```

Handler in `handlers/start.py`:

```python
import telekit

class EchoHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        cls.on.text().invoke(cls.echo)

    def echo(self) -> None:
        self.chain.sender.set_text(f"{self.message.text}!")
        self.chain.send()
```

## Single-file bot Example

```python
import telekit

class NameHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        @cls.on.text("My name is {name}")
        def _(message: telebot.types.Message, name: str):
            cls(message).handle(name, None)

    def handle(self, name: str) -> None: 
        self.chain.sender.set_text(f"👋 Hello {name}!")
        self.chain.send()

telekit.Server("TOKEN").polling()
```

You’re free to decide)

[Next: Senders »](3_senders.md)