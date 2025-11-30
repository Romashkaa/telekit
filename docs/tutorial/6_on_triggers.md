# Message Handling (Triggers) 

Telekit provides a simple way to work with incoming messages using decorators.  
Below are two main types, but there are many more:

- `on.text` — handle messages based on text patterns  
- `on.command` — handle commands (like `/start`, `/help`)  

---

## `on.text(*patterns, chat_types=None, whitelist=None)`

Handles messages that match one or more text patterns.
You can pass a simple string, e.g., `"hello"`, and the bot will respond to exact matches.

```python
class HelloHandler(telekit.Handler):
    @classmethod
    def init_handler(cls) -> None:
        cls.on.text("Hello").invoke(cls.say_hello)

    def say_hello(self, message):
        self.chain.sender.set_text("Hello! Nice to see you 😄")
        self.chain.send()
```
  
Patterns can also include placeholders in curly braces `{name}` — they will be passed to the handler as arguments.

```python
class NameHandler(telekit.Handler):
    @classmethod
    def init_handler(cls) -> None:
        cls.on.text("My name is {name}", "I am {name}").invoke(cls.handle_name)

    def handle_name(self, message, name: str):
        self.chain.sender.set_text(f"Hello, {name}!")
        self.chain.send()
```

If you call `on.text()` **without any patterns**, the bot will intercept **all messages**.  

Other parameters:
- **patterns** — text patterns or simple strings  
- **chat_types** — list of chat types (`'private'`, `'group'`)  
- **whitelist** — list of chat IDs where the handler is active  

---

## Using as a Decorator or Method

Triggers can be used in two ways:

1. **Decorator-style** — attach directly to a method:
```python
@cls.on.text("Hello")
def say_hello(message):
    ...
```

2. **Method-style with `.invoke()`** — attach a handler function dynamically:
```python
cls.on.text("Hello").invoke(cls.say_hello) # only `cls.*`
```

---

[See all triggers](../documentation/6_on_triggers.md)
[Next: Chain »](7_chain.md)

