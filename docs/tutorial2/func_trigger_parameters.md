# Func Trigger

The `on.func` trigger allows you to define **custom matching logic** using a Python function.  
This trigger is activated when the provided function returns `True` for an incoming message.

This is useful for:
- complex conditions
- filtering by message content, metadata, or custom rules  
- validating formats (numbers, emails, commands, etc.)

## Basic Example

React only to messages that contain **digits**:

```python
import telekit

class NumberHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        # Trigger when message.text exists and contains only digits
        cls.on.func(
            lambda message: message.text is not None and message.text.isdigit()
        ).invoke(cls.handle)

    def handle(self) -> None:
        self.chain.sender.set_text("🔢 You sent a number!")
        self.chain.send()

telekit.Server(BOT_TOKEN).polling()
```

Here:

- `on.func(...)` receives a function that takes a **Message** object  
- If the function returns **True**, the trigger fires
- The specified handler method (`handle`) is invoked

# Parameters

When using `on.func`, you can pass **additional arguments** to your `handle` method using `invoke_args` and `invoke_kwargs`.

```python
cls.on.func(
    lambda message: message.text is not None and message.text.isdigit(),
    invoke_args=[100],                 # positional argument(s) passed to the 'handle' method
    invoke_kwargs={"flag": True}       # keyword argument(s) passed to the 'handle' method
).invoke(cls.handle)
```

Here:

- `invoke_args` – a list or tuple of **positional arguments** that will be passed to your `handle` method.
- `invoke_kwargs` – a dictionary of **keyword arguments** that will also be passed to the  `handle` method.


## Named Methods

For better readability, you can pass a regular method instead of lambda:

```python
class NumberHandler(telekit.Handler):

    @classmethod
    def is_number(cls, message) -> bool:
        return message.text is not None and message.text.isdigit()

    @classmethod
    def init_handler(cls) -> None:
        cls.on.func(cls.is_number).invoke(cls.handle)

    def handle(self) -> None:
        self.chain.sender.set_text("Valid number received.")
        self.chain.send()
```

This approach is recommended for **complex validation logic**.

> [!TIP]  
> Keep functional conditions **pure and fast**.
> Slow or blocking logic inside `on.func` may delay message processing.