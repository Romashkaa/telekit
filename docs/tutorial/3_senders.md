# Senders

Senders in Telekit provide a high-level interface for sending and managing messages in Telegram bots. They wrap the standard TeleBot API, adding convenience features such as temporary messages, automatic editing, error handling, formatting, adding photos and effects.

## Basic Usage 

Use `self.chain.sender.*` to define how your bot responds.

There are two main ways to create a message: a simple text message or a structured message with a title and body:

- A simple text message:
    - `set_text(text)`: Update the message text (regular).
- Or let Telekit handle the layout for you: 
    - `set_title(title)` and `set_message(message)`
    - `set_use_italics(True)` – Enable italics for the message body.
    - `set_use_newline(False)` – Disable spacing between title and message.

Example:

```python
self.chain.sender.set_text("Hola! Something...")
# OR
self.chain.sender.set_title("Hola!")
self.chain.sender.set_message("Something below...")
```

You can also add a line at the end without effort:

```python
self.chain.sender.append("\nNew Line!")
```

Use structured messages when you want to separate the main title from additional content. Simple messages are best for quick replies.

## Formatting & Replying

Telekit supports text formatting and replying to specific messages:

- `set_parse_mode(mode)`: Set formatting mode.
- `set_reply_to(message)`: Reply to a specific message.

> [!TIP]
> See more methods and features in the [documentation](../documentation/3_senders.md)

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
self.chain.sender.set_effect(self.chain.sender.Effect.FIRE)
```

## Chat Actions

To send a chat action (typing indicator, upload status, etc.), use the
send_chat_action(action) method. The action argument can be either a string or a ChatAction enum value.

> Using ChatAction from the sender
```py
self.chain.sender.send_chat_action(self.chain.sender.ChatAction.UPLOAD_AUDIO)
self.chain.sender.send_chat_action("upload_audio")
```

> Importing ChatAction directly
```py
from telekit.types import ChatAction
self.chain.sender.send_chat_action(ChatAction.TYPING)
```

> [!TIP]
> Chat actions are useful for long-running operations to let the user know the bot is working (e.g. database queries, file uploads, API calls).

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
        sender = self.chain.create_sender()
        sender.set_text("✅ Message sent")
        sender.send_or_handle_error()

        sender.set_text("🔴 Second message <b>Unclosed tag") # automatically handles the error
        sender.send_or_handle_error()

telekit.Server("BOT_TOKEN").polling()
```

## Using Sender as a Context Manager

Senders can also be used as context managers. This form **does NOT automatically send** the message.  
It only groups your setter calls in a clean block:

```python
with self.chain.sender as sender:
    sender.set_title("Hello!")
    sender.set_message("It's Telekit.")
```

You still need to call `self.chain.send()` or `sender.send()` afterward.

> [!TIP]
> See more info in the [documentation - Context Manager](../documentation/3_senders.md#context-manager)

---

## Example: Sending Ads to Multiple Chats

This example shows how to send an announcement to several chats and notify the admin about the result.

```python
import telekit

class AdHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        # Only Admin Command ↴
        cls.on.command("ad", whitelist=[1489794]).invoke(cls.ad)

    def ad(self):
        # list of chat IDs to send the ad
        chat_ids: list[int] = [123456789, 987654321]
        recipients: int     = 0

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

## Example: `append` method

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
        self.chain.sender.append(f"{char}")    # HERE
        self.chain.edit()
```

- [Senders documentation: See more methods and features](../documentation/3_senders.md)
- [Next: Text Styling »](4_text_styling.md) 
