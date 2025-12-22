## Handler

The `Handler` class in Telekit serves as the base for all bot message handlers.  
It provides a structured way to manage incoming messages, commands, and user interactions.  

Each subclass of `Handler` should implement its own logic by overriding `init_handler(cls)` to register triggers and defining instance methods to handle the responses. 

### Example: Text Pattern Handling

```python
import telekit

class OnTextHandler(telekit.Handler):

    # Initialize the message handlers
    @classmethod
    def init_handler(cls) -> None:
        cls.on.text("Name: {name}. Age: {age}").invoke(cls.handle)

    # Handle logic
    def handle(self, name: str | None, age: str | None) -> None: 

        if not name: 
            name = self.user.username

        if not age:
            age = "An unknown number of"

        self.chain.sender.set_title(f"Hello {name}!")
        self.chain.sender.set_message(f"{age} years is a wonderful stage of life!")
        self.chain.send()
```

- [Learn more about Handler](../documentation/5_handler.md)
- [Next: Triggers »](6_on_triggers.md)