# Receiving Messages and Files in Telekit

Telekit provides flexible decorators to handle various types of user input, from plain text to documents. These tools make it easy to process messages without manually parsing updates or managing states.

## Receive Any Message Type

Use `@self.chain.entry()` to handle any message type. You can add a `filter_message` to process only messages that meet certain conditions (e.g., containing text).

```python
@self.chain.entry(
    filter_message=lambda message: bool(message.text),  # Only messages with text
    delete_user_response=True                           # Automatically delete user's message
)
def handler(message):
    print(message.text)  # Process the message
```

## Receive Text Messages

Use `@self.chain.entry_text()` when you expect the user to send a text message and want Telekit to automatically extract it.

```python
@self.chain.entry_text()
def text_handler(message, text: str):
    print(text)  # The text content is passed directly as `text`
```

### Suggested Inline Options (Quick Replies)

You can provide suggested replies for the user to click instead of typing:

```python
self.chain.set_entry_suggestions(["Suggestion 1", "Suggestion 2"])
```

> [!WARNING]
> Entry suggestions are mutually exclusive with inline keyboards  
> (e.g. `set_inline_keyboard`).

## Receive Documents

### Specific File Types

Use `@self.chain.entry_document()` to handle file uploads and filter by extension.

```python
@self.chain.entry_document(allowed_extensions=(".zip",))
def doc_handler(message: telebot.types.Message, document: telebot.types.Document):
    print(document.file_name, document)
```

### Text Documents with Auto-Detected Encoding

Telekit can automatically decode text files using `@self.chain.entry_text_document()`. It supports multiple file types like `.txt`, `.py`, `.js`, etc.

```python
@self.chain.entry_text_document(allowed_extensions=(".txt", ".js", ".py"))
def text_document_handler(message, text_document: telekit.types.TextDocument):
    print(
        text_document.text,      # The content of the file
        text_document.file_name, # Name of the uploaded file
        text_document.encoding,  # Detected encoding
        text_document.document   # Original <telebot.types.Document> object
    )
```

> [!NOTE]
> You can explore all available entry types directly in the code by typing `self.chain.entry_` and checking the currently supported options.

## Combination

Entries can be combined with inline keyboards or entry suggestions to create a more intuitive user experience:

```py
def handle(self):
    self.set_inline_keyboard(
        {
            "Cancel": self.cancel_entry
        }
    )
    @self.chain.entry_text()
    def text_handler(message, text: str):
        self.entered_text = text
        ...
```

In this setup, Telekit automatically decides which handler to invoke:
— if the user clicks an inline button, the `self.cancel_entry` callback is executed;
— if the user types a message, the `text_handler` processes the input.

## Other Handlers

Telekit provides a set of specialized entry handlers for different message types:

- `set_entry` - general callback for any message.
- `set_entry_text` - callback for text messages only.
- `set_entry_photo` - callback for photo messages.
- `set_entry_document` - callback for document messages.
- `set_entry_text_document` - callback for text-based documents; auto-downloads and decodes text.
- `set_entry_location` - callback for location messages.
- Each of these methods has a corresponding decorator with the same name, but without the `set_` prefix.
    - Setter:
    ```python
    def handle_name(self, message: Message, name: str):
        print(name)

    def handle(self):
        ...
        self.chain.set_entry_text(self.handle_name) # self.handle_name: Callable[[Message, name], Any]
        self.chain.send()
    ```
    - Decorator:
    ```py
    def handle(self):
        ...
        @self.chain.entry_text()
        def _handle_name(message: Message, name: str):
            print(name)
            
        self.chain.send()
    ```

## Example

```python
import telekit

class NameHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        cls.on.text("My name is {name}").invoke(cls.display_name)

    def display_name(self, name: str) -> None:
        self.chain.sender.set_title(f"Hello {name}!")
        self.chain.sender.set_message("Your name has been set. You can change it below if you want")
        self.chain.set_inline_keyboard(
            {
                "✏️ Change": self.change_name
            }
        )
        self.chain.edit()

    def change_name(self):
        self.chain.sender.set_title("⌨️ Enter your new name")
        self.chain.sender.set_message("Please type your new name below:")

        @self.chain.entry_text(delete_user_response=True)
        def name_handler(message, name: str):
            self.display_name(name)

        # name suggestions
        self.chain.set_entry_suggestions(["Romashka", "Felix"])

        self.chain.edit()

telekit.Server("TOKEN").polling()
```

[Next: Triggers »](6_on_triggers.md)