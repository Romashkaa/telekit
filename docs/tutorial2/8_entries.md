# Entries

Telekit provides flexible methods to handle various types of user input, from plain text to documents. These tools make it easy to process messages without manually parsing updates or managing states.

```python
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
        self.chain.sender.set_title("⌨️ Enter name")
        self.chain.sender.set_message("Enter the name to be displayed in the bot")
        self.chain.set_entry_text(
            self.handle_entered_name, 
            delete_user_response=True
        )
        self.chain.edit()

    def handle_entered_name(self, message, name: str):
        self.display_name(name)

telekit.Server("TOKEN").polling()
```

Explanation:

- The bot listens for messages that match the pattern `"My name is {name}"`.  
- When such a message is received, `display_name` is called with the captured `name`.  
- It greets the user using the captured name.
- `set_inline_keyboard` adds a button labeled `"✏️ Change"`, which calls the `change_name` method when pressed.  
- In `change_name`, the bot prompts the user and sets up an entry field using `set_entry_text`.  
- `delete_user_response=True` ensures that the user's entered text is deleted after being received.
- Once the user enters a name, `handle_entered_name` is invoked, which in turn calls `display_name` with new received name.  
- `self.chain.edit()` updates the previous bot message instead of sending a new one.

This structure allows the bot to greet users dynamically by name, provide an inline button to change the name, and update the original message in place rather than sending multiple messages.

## Input Types

The most popular entry types:

<details>
<summary><code>entry</code> – receive any messages</summary>

Use `@self.chain.entry()` to handle any message type. You can add a `filter_message` to process only messages that meet certain conditions (e.g., containing text).

```python
@self.chain.entry(
    filter_message=lambda message: bool(message.text),  # Only messages with text
    delete_user_response=True                           # Automatically delete user's message
)
def handler(message):
    print(message.text)  # Process the message
```

</details>

<details>
<summary><code>entry_text</code> – receive text messages</summary>

Use `@self.chain.entry_text()` when you expect the user to send a text message and want Telekit to automatically extract it.

```python
@self.chain.entry_text()
def text_handler(message, text: str):
    print(text)  # The text content is passed directly as `text`
```

You can provide suggested replies for the user to click instead of typing:

```python
self.chain.set_entry_suggestions(["Suggestion 1", "Suggestion 2"])
```

</details>

<details>
<summary><code>entry_document</code> – receive document</summary>

Use `@self.chain.entry_document()` to handle file uploads and filter by extension.

```python
@self.chain.entry_document(allowed_extensions=(".zip",))
def doc_handler(message: telebot.types.Message, document: telebot.types.Document):
    print(document.file_name, document)
```

</details>

<details>
<summary><code>entry_text_document</code> – receive text document</summary>

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

</details>

> [!NOTE]
> You can explore all available entry types directly in the code by typing `self.chain.entry_` and checking the currently supported options.

## Direct Callbacks

In Telekit, you can handle user input **not only with decorators**, but also by using the corresponding **setter methods** with the `set_` prefix.

For example, instead of using `@self.chain.entry_text()`, you can use `self.chain.set_entry_text()`:

<details>
<summary>Setter version</summary>

```py
def handle_name(self, message: Message, name: str):
    print(name)

def handle(self):
    self.chain.set_entry_text(self.handle_name)
    self.chain.send()
```

</details>

<details>
<summary>Decorator version</summary>

```py
def handle(self):
    @self.chain.entry_text()
    def _handle_name(message: Message, name: str):
        print(name)
        
    self.chain.send()
```
</details>

The available non-decorator entry methods are:

- `set_entry` — general callback for any message  
- `set_entry_text` — callback for text messages only  
- `set_entry_photo` — callback for photo messages  
- `set_entry_document` — callback for document messages  
- `set_entry_text_document` — callback for text-based documents; automatically downloads and decodes text  
- `set_entry_location` — callback for location messages

## Entries + Inline Keyboards

Entries can be combined with inline keyboards to create a more intuitive user experience:

```py
def handle(self):
    self.set_inline_keyboard(
        {
            "Cancel": self.cancel_entry
        }
    )
    self.chain.set_entry_text(self.handle_text)
```

In this setup, Telekit automatically decides which handler to invoke:
— if the user clicks an inline button, the `self.cancel_entry` callback is executed;
— if the user types a message, the `self.handle_text` processes the input.

<details>
<summary>Example</summary>

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

</details>