# Basic Handler

Handler is a class that defines the logic for processing incoming updates from the server.

Think of a handler as a specialized administrator in an office: each one is **responsible for a specific task** (for example, user registration or profile settings), and triggers are the rules the administrator uses to decide which desk a client's request should be directed to.

Instead of registering separate handler functions all over your code, Telekit groups the logic into classes that inherit from `telekit.Handler`:

- **The class method `init_handler(cls)`** is called when the server is initialized. This is where you register all triggers using the `cls.on` object.
- **The instance method `handle(self)`** contains the actual request-processing logic. Note that the trigger automatically creates a new instance of the class for each update.

For example, handling the `/start` command:

```python
import telekit

class MyHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        # here we’ll define message triggers
        cls.on.command("start").invoke(cls.handle)

    def handle(self):
        self.chain.sender.set_text("Hello!")
        self.chain.send()

telekit.Server(BOT_TOKEN).polling()
```

Here:
1. We define a handler class `MyHandler` that inherits from `telekit.Handler`.  
   The class name can be anything, but there must not be two handlers with the same name in the project.

2. In the special class method `init_handler`, we register a trigger that listens for the `/start` command  
   and specifies that the `handle` method should be invoked when this command is received.

3. In the `handle` method, we construct a simple `"Hello!"` message and send it to the user.

4. The `init_handler` method is called when an instance of the `Server` class is created.

> [!IMPORTANT]
> The trigger automatically creates an instance of the `MyHandler` class.  
> That is why `handle` is defined as an instance method (using `self`),  
> but is passed to the trigger via `cls.handle`.

## Triggers at a glance

The `on` object offers many ways to intercept messages:

- `cls.on.command("start")` — reacts to commands.
- `cls.on.text("hi", "hello")` — reacts to specific text (case-insensitive).
- `cls.on.text()` — intercepts any text message.
- `cls.on.photo()`, `cls.on.regexp(r"...")`, `cls.on.func(...)` — filter by media, regular expressions, or arbitrary Python functions.

[Next: Triggers »](3_triggers.md)