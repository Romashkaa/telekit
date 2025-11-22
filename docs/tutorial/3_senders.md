# Senders

Senders in Telekit provide a high-level interface for sending and managing messages in Telegram bots. They wrap the standard TeleBot API, adding convenience features such as temporary messages, automatic editing, error handling, formatting, adding photos and effects.

## Basic Usage 

You use `self.chain.sender.*` to define how your bot responds.

There are two main ways to create a message: a simple text message or a structured message with a title and body:

- A simple text message:
    - `set_text(text)`: Update the message text (regular).
- Or let Telekit handle the layout for you: 
    - `set_title(title)` and `set_message(message)`
    - `set_use_italics(...)` – Enable/disable italics for the message body.
    - `set_add_new_line(...)` – Add/remove a blank line between title and message.

Example:

```python
self.chain.sender.set_text("Hola! Something...")
# OR
self.chain.sender.set_title("Hola!")
self.chain.sender.set_message("Something below...")
```

You can also add a line at the end without effort:

```python
self.chain.sender.add_message("\nNew Line!")
```

Use structured messages when you want to separate the main title from additional content. Simple messages are best for quick replies.

## Formatting & Replying

Telekit supports text formatting and replying to specific messages:

- `set_parse_mode(mode)`: Set formatting mode.
- `set_reply_to(message)`: Reply to a specific message.
- `set_photo(photo)`: Attach a photo to your message:

## Photos & Effects

You can attach photos or apply visual effects to make messages more engaging:

- `set_photo(photo)`: Attach a photo. The source can be:

```python
self.chain.sender.set_photo("https://...") # Internet -> Telegram (fast)
self.chain.sender.set_photo("С:/...")      # Your PC  -> Telegram (slow)
self.chain.sender.set_photo("file_id")     # Telegram -> Telegram (super fast)
```

- `set_effect(effect)`: Apply a visual effect:
- `Effect.*`: Effect to apply:

```python
self.chain.sender.set_effect(self.chain.sender.Effect.FIRE) # only 1 from 6
```

## Under-the-Hood Methods

These settings are handled automatically, but you can override them if needed:

- `set_chat_id(chat_id)`: Change target chat.
- `set_edit_message(message)`: Set the message to edit.
- `set_reply_markup(reply_markup)`: Add inline/keyboard markup. Raw.

## Advanced Tools

Telekit provides advanced tools for managing messages and errors:

- `get_message_id(message)`: Get the ID of a message.
- `delete_message(message)`: Delete a message.
- `set_temporary(flag)`: Mark message as temporary.
- `set_delete_temporaries(flag)`: Delete previous temporary messages after a new one is sent.
- `error(title, message)`: Send a custom error (не впливає на збережені title та message).
- `pyerror(exception)`: Send exception details.
- `send_or_handle_error()`: Send a message and show a Python exception if it fails.
- `try_send()`: Attempt sending, returns `(message, exception)`.
- `send()`: Send or edit the message. Returns None if it fails.

## Creating a New Sender

You can create independent senders to send messages to different users or chats.
This is useful when sending notifications to multiple recipients or handling separate conversations.

```python
import telekit

class NameHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        cls.on.text().invoke(cls.greet)

    def greet(self):
        sender = self.chain.create_sender() # 1st way
        sender.set_text("✅ First sender")
        sender.send_or_handle_error()

        sender2 = telekit.senders.AlertSender(self.chain.chat_id) # 2nd way
        sender2.set_text("✅ Second sender")
        sender2.send_or_handle_error()

        sender2.set_text("🔴 Second sender <b>Unclosed tag")
        sender2.send_or_handle_error()

telekit.Server("BOT_TOKEN").polling()
```

---

## Example: Sending Ads to Multiple Chats

This example shows how to send an announcement to several chats and notify the admin about the result.

```python
import telekit

class NameHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        # Only Admin Command ↴
        cls.on.command("ad", whitelist=[1489794]).invoke(cls.ad)

    def ad(self):
        # list of chat IDs to send the ad
        chat_ids = [123456789, 987654321]
        recipients  = 0

        for chat_id in chat_ids:
            sender = self.chain.create_sender(chat_id)
            sender.set_title("⚠️ Attention!")
            sender.set_message("This is an important announcement.")
            if sender.send_or_handle_error():
                recipients += 1

        # notify the admin
        self.chain.sender.set_title("✅ Success")
        self.chain.sender.set_message(f"Your ad has been sent to {recipients} recipients.")
        self.chain.sender.set_effect(self.chain.sender.Effect.FIRE)
        self.chain.send()
```

- `add_message` method + styling

```python
import telekit

from telekit.styles import Group, Sanitize, Quote

class Start(telekit.Handler):
    @classmethod
    def init_handler(cls) -> None:
        cls.on.command("start").invoke(cls.start)

    def start(self):
        self.chars = iter("ROMASHKA")

        self.chain.sender.set_title(Group("Hello, ", Sanitize(self.user.first_name), "!"))
        self.chain.sender.set_message(
            "Quote of the Day:\n",
            Quote("The only way out is through."),
            "- "
        )
        self.chain.sender.set_use_italics(False)
        self.chain.set_timeout(self.update, 1)
        self.chain.send()

    def update(self):
        char = next(self.chars, None)

        if not char:
            return
        
        self.chain.set_timeout(self.update, 1)
        self.chain.sender.add_message(f"{char}")
        self.chain.edit()
```

[Text Styling »](4_text_styling.md) 
