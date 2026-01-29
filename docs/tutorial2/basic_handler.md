# Basic Handler

Handler is a class that defines the logic for processing incoming updates from the server.
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

[Next: Triggers »](triggers.md)