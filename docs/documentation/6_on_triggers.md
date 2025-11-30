# Triggers (`On` class)

This section lists all triggers available in Telekit for handling messages and commands.

---

## All Triggers

- `on.message(self, commands=None, regexp=None, func=None, content_types=None, chat_types=None, whitelist=None, **kwargs)` - registers a handler for any type of message; supports commands, regex patterns, content types, chat types, and whitelist restrictions  
- `on.text(self, *patterns, chat_types=None, whitelist=None)` - decorator for handling messages that match text patterns; supports placeholders like `{name}` and exact string matches  
- `on.command(self, *commands, chat_types=None, whitelist=None, **kwargs)` - registers a handler for Telegram commands starting with `/`  
- `on.regexp(self, regexp, chat_types=None, whitelist=None, **kwargs)` - registers a handler triggered when a message matches a regular expression  
- `on.photo(self, chat_types=None, whitelist=None, **kwargs)` - registers a handler for incoming photos

---

## Usage

Triggers can be used in two ways:

1. **Decorator-style** — attach directly to a function:

```python
@cls.on.text("Hello")
def say_hello(message):
    cls(message).chain.sender.set_text("Hello!")
    cls(message).chain.send()
```

2. **Method-style with `.invoke()`** — attach a handler mathod:

```python
cls.on.text("Hello").invoke(cls.say_hello)  # only works with `cls.*`
```

- Here, `cls` refers to a subclass of the `Handler` class.
- Both approaches allow flexible and clean registration of message triggers, making it easy to handle different inputs and commands in your bot.

[See tutorial](../tutorial/6_on_triggers.md)