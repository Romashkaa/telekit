# Senders

Senders in Telekit provide a high-level interface for sending and managing messages in Telegram bots. They wrap the standard TeleBot API, adding convenience features such as temporary messages, automatic editing, error handling, formatting, adding photos and effects.

```python
import telekit

class EchoHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        cls.on.text().invoke(cls.echo) # accepts all text messages

    def echo(self) -> None:
        self.chain.sender.set_text(f"{self.message.text}!")
        self.chain.send()

telekit.Server("TOKEN").polling()
```

> Use this echo bot example to test any method from this page

## Send Text Messages

There are two main ways to create a message: a **plain text message** or a structured **message with a title and body**:

<details>
<summary>Plain Text Message</summary>

Use `set_text()` to send a plain text message to the chat:

```py
self.chain.sender.set_text("Hola!")
self.chain.send()
```

`set_text()` also supports multiple text parts.
All parts are automatically joined using the `sep` parameter.

```py
self.chain.sender.set_text(
    "Hello", "World!", 
    sep=" "
)
self.chain.send()
```

> ![Result](hello_world.png)
</details>

<details>
<summary>Message with a Title and Body</summary>

Use a structured message when you want to separate a **title** from the **message body**.
This layout is useful for notifications, and other messages.

```py
self.chain.sender.set_title("Hello!")
self.chain.sender.set_message("This is the message body.")
self.chain.send()
```

By default:
- The **title** is rendered in bold
- The **message body** is rendered below title
- A blank line is inserted between them

> [!NOTE]
> `set_message()` and `set_title()` also support multiple text parts. All parts are automatically joined using the `sep` parameter.

You can fine-tune the appearance using sender options:

```py
self.chain.sender.set_title("Hello!")
self.chain.sender.set_message("This is the message body.")

self.chain.sender.set_use_italics(True)    # enable italics for body
self.chain.sender.set_use_newline(False)   # disable spacing between title and message

self.chain.send()
```

Use **title + body** messages when:
- You want a clear visual hierarchy
- The message has a heading and explanation
- You are building menus

For quick replies or single-line messages, prefer `set_text()` instead.

</details>

<details>
<summary>Append Additional Text</summary>

Append additional text to the current message content:

```py
self.chain.sender.set_text("Hello")
self.chain.sender.append(", how are you?")
self.chain.sender.append(" Fine?")
self.chain.send()
```

> Useful for building messages in a for-loop.
</details>

<details>
<summary>Removing Text Content</summary>

You can remove text content using `remove_text()`:

```py
self.chain.sender.remove_text()  # clears title, message and text
```

By default, `sender.remove_text()` is called automatically after each `send()` to prevent text from carrying over to subsequent messages in the same chain.

Use `sender.set_remove_text(False)` to preserve the same text across multiple sends:

```py
import telekit
import time

class MyHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        cls.on.text().invoke(cls.handle) # accepts all text messages

    def handle(self) -> None:
        self.chain.sender.set_remove_text(False) # try disabling and enabling

        self.chain.sender.set_text("Pinned title")
        self.chain.send()

        for _ in range(10):
            time.sleep(1) # wait 1 second
            self.chain.sender.append("!") # appends "!" to the message text
            self.chain.edit() # edit previous message

telekit.Server("TOKEN").polling()
```

</details>

## Attach Media to Messages

<details>
<summary>Photos</summary>

To attach a photo to your message, simply call the `set_photo()` method before sending.

```py
self.chain.sender.set_photo("greeting.png")
self.chain.sender.set_text("Welcome here!")
self.chain.send()
```

- Supported photo sources:
  - Local file path (e.g. `"greeting.png"`)
  - Direct URL (e.g. `"https://...jpg"`)
  - Telegram `file_id` (previously uploaded files)

> [!TIP]
> Using a Telegram `file_id` is the fastest option, as the file is already hosted on Telegram's servers.

</details>

<details>
<summary>Documents</summary>

Use `set_document()` to attach a file to message

```py
self.chain.sender.set_document("file.pdf")
self.chain.sender.set_text("See attached document.")
self.chain.send()
```

Use `set_text_as_document()` to send text as a document:

```py
self.chain.sender.set_text_as_document("This is the content of the document.")
self.chain.sender.set_text("See attached text document.")
self.chain.send()
```

</details>

<details>
<summary>Videos</summary>

Attach a video file using `set_video()` before sending:

```py
self.chain.sender.set_video("cats.mp4")
self.chain.sender.set_text("Watch this video!")
self.chain.send()
```

> Supported sources are local paths, URLs, or Telegram file IDs.

</details>

<details>
<summary>Video Notes</summary>

Send circular video notes with `set_video_note()`:

```py
self.chain.sender.set_video_note("video_note.mp4")
self.chain.send()
```

> Video notes are short, round videos.

</details>

<details>
<summary>Animation</summary>

Send GIF animations using `set_animation()`:

```py
self.chain.sender.set_animation("funny.gif")
self.chain.send()
```

> Animations support the same sources as photos and videos.

</details>

<details>
<summary>Audio</summary>

Attach audio files with `set_audio()`:

```py
self.chain.sender.set_audio("Romashka - R2 (CDs).mp3")
self.chain.send()
```

> Useful for sending music or sound clips.

</details>

<details>
<summary>Voice</summary>

Send voice messages using `set_voice()`:

```py
self.chain.sender.set_voice("voice.ogg")
self.chain.send()
```

> Voice messages are short audio clips.

</details>

<details>
<summary>Media Groups</summary>

Send multiple media items as a group using `set_media()`:

```py
from telebot.types import InputMediaPhoto, InputMediaVideo

media = [
    InputMediaPhoto("photo1.jpg"),
    InputMediaPhoto("https://example.com/photo2.jpg"),
    InputMediaVideo(open("video.mp4", "rb"))
]

self.chain.sender.set_media(*media)
self.chain.send()
```

> Media groups send multiple items in a single message.

</details>

<details>
<summary>Removing Attachments</summary>

Remove any attached media or documents before sending with `remove_attachments()`:

```py
self.chain.sender.set_photo("photo.jpg")
self.chain.sender.remove_attachments()  # clears photo
self.chain.sender.set_text("There's no photo ;)")
self.chain.send()
```

> Useful when you want to clear previous attachments.

By default, `sender.remove_attachments()` is called automatically after each `send()` to prevent attached media from carrying over to subsequent messages in the same chain. 

Use `sender.set_remove_attachments(False)` to preserve attachments across multiple sends:

```py
self.chain.sender.set_photo("photo.jpg")
self.chain.sender.set_text("^- photo...")
self.chain.sender.set_remove_attachments(False)
self.chain.send()

self.chain.sender.set_text("^- the same photo...")
self.chain.send()
```

</details>

## Message Control

<details>
<summary>set_parse_mode</summary>

Set the parse mode for message formatting (e.g., Markdown, HTML).

By default, the parse mode is **HTML**, but all strings are **automatically escaped**. This means special characters like `<`, `>`, `&` are safe to pass as plain text.

To use raw formatting tags, disable escaping explicitly:

```py
self.chain.sender.set_parse_mode("markdown") # you can also use markdown (v2)
self.chain.sender.set_text("*Bold text* and _italic text_.", escape=False) # disable auto-escaping for strings
self.chain.send()
```

> [!WARNING]
> When using `escape=False`, make sure your string is already valid for the current parse mode.

Or wrap the string in `Raw(...)` to skip escaping for a single value:

```py
from telekit.styles import Raw
self.chain.sender.set_text(Raw("<b>Bold text</b>"), " plain text")
```

You can also use constants to change the parse mode:

```py
from telekit.types import ParseMode
self.chain.sender.set_parse_mode(ParseMode.HTML)
```

> Choose the appropriate parse mode for your formatting needs.

</details>

<details>
<summary>set_reply_to</summary>

Make the message a reply to another message object:

```py
self.chain.sender.set_reply_to(self.message) # reply to the user's initial message
self.chain.sender.set_text("Replying to your message.")
self.chain.send()
```

> Replies help maintain conversation context.

</details>

<details>
<summary>set_reply_to_message_id</summary>

Reply by specifying the message ID directly:

```py
self.chain.sender.set_reply_to_message_id(self.message.message_id) # reply to the user's initial message
self.chain.sender.set_text("Reply by message ID.")
self.chain.send()
```

> Use when you only have the message ID.

</details>

<details>
<summary>set_edit_message</summary>

Edit an existing message object instead of sending a new one:

```py
self.chain.sender.set_edit_message(message)
self.chain.sender.set_text("Edited message content.")
self.chain.send()
```

> Edits modify the content of an existing message.

</details>

<details>
<summary>set_edit_message_id</summary>

Edit a message by specifying its ID:

```py
self.chain.sender.set_edit_message_id(message.message_id)
self.chain.sender.set_text("Edit by message ID.")
self.chain.send()
```

> Useful when you only know the message ID.

</details>

<details>
<summary>set_chat_id</summary>

Specify the chat ID to send or edit the message in:

```py
self.chain.sender.set_chat_id(472584)
self.chain.sender.set_text("Message to specific chat.")
self.chain.send()
```

> Overrides the default chat ID (`self.message.chat.id`).

</details>

## Effects

<details>
<summary>set_effect</summary>

Apply an effect to an message using enum, string, or integer: 

```py
from telekit.types import Effect

self.chain.sender.set_effect(Effect.FIRE)
self.chain.sender.set_text("🔥 Fire!")
self.chain.send()
```

**Available Effects:**
- `FIRE` - 🔥
- `PARTY` - 🎉
- `HEART` - ❤️
- `THUMBS_UP` - 👍
- `THUMBS_DOWN` - 👎
- `POOP` - 💩

</details>

<details>
<summary>set_message_effect_id</summary>

Apply an effect to an message by its ID:

```py
self.chain.sender.set_message_effect_id(5104841245755180586)
self.chain.sender.set_text("🔥 Fire!")

self.chain.send()
```

**Available Effects:**
- Fire - 🔥 (`"5104841245755180586"`)
- Party - 🎉 (`"5046509860389126442"`)
- Heart - ❤️ (`"5159385139981059251"`)
- Thumbs Up - 👍 (`"5107584321108051014"`)
- Thumbs Down - 👎 (`"5104858069142078462"`)
- Poop - 💩 (`"5046589136895476101"`)

</details>

## Temporary Messages

Temporary messages are messages marked for later deletion and managed automatically during sending.

<details>
<summary>set_temporary</summary>

Mark the current message as temporary. It will be deleted later if `set_delete_temporaries(True)` is enabled:

```py
self.chain.sender.set_temporary(True)
self.chain.sender.set_text("This message will be temporary.")
self.chain.send()
```

> [!IMPORTANT] 
> Only flags the message as temporary; deletion happens during sending next message.

</details>

<details>
<summary>set_delete_temporaries</summary>

Enable deletion of previously marked temporary messages in the current chat:

```py
self.chain.sender.set_delete_temporaries(True) # `True` by default
self.chain.sender.set_text("This message triggers deletion of previous temporary messages.")
self.chain.send()
```

> Deletion of previous temporary messages occurs when sending the current message.

> [!IMPORTANT] 
> - `set_temporary()` only marks the current message.  
> - `set_delete_temporaries()` only triggers deletion of earlier marked messages.

</details>

## Action Methods

These methods do not configure the current message; instead, they perform a specific action immediately.

<details>
<summary>send_chat_action</summary>

Send chat actions like typing indicators:

```py
from telekit.types import ChatAction

self.chain.sender.send_chat_action(ChatAction.TYPING)
```

> Shows the bot is performing an action.

</details>

<details>
<summary>send_emoji_game</summary>

Send a dice message with the given emoji and returns the game result.

Currently, emoji must be one of `🎲 🎯 🏀 ⚽ 🎳 🎰`:

```py
from telekit.dices import SlotMachine

result: SlotMachine = self.chain.sender.send_emoji_game("🎰")

print(
    f"\n{result.value=}", # Raw dice value: 1-64
    f"\n{result.slots=}", # Reel values as a tuple: (2, 1, 4)

    f"\n{result.is_win=}", # Corresponds to the red indicator
    f"\n{result.is_jackpot=}\n", # True only for "7️⃣7️⃣7️⃣"
    f"\n{result.rank=}", # 'nothing', 'pair', 'triple', 'double_7' or 'triple_7'

    f"\n{result.emojis=}", # Visual representation: "🍒7️⃣🍋"
    f"\n{result.split_names=}" # Reel names: ("cherry", "seven", "lemon")
)
```

> [!TIP]
> Prefer using the specific methods (e.g. `send_dice()`, `send_slot_machine()`) for typed return values. Use this method only when the emoji is dynamic.

</details>

<details>
<summary>delete_message</summary>

Deletes a message, optionally ignoring bot messages.

```py
self.chain.sender.delete_message(message, only_user_messages=False)
```

**Parameters:**
- `message: Message | None` — The message to delete.
- `only_user_messages: bool` — If `True`, only deletes user messages.
</details>

<details>
<summary>send_pyerror</summary>

Sends a Python exception as a message.

```py
try:
    ...
except Exception as exception:
    self.chain.sender.send_pyerror(exception)
```

</details>

<details>
<summary>send_error</summary>

Sends a custom error message.

```py
self.chain.sender.send_error("Error Heading", "Something went wrong...")
```

**Parameters:**
- `title: str | TextEntity` — The title of the error.
- `message: str | TextEntity` — The error message body.
</details>

<details>
<summary>get_message_id</summary>

Retrieves the message ID from a `Message` object.

```py
msg_id = self.chain.sender.get_message_id(message)
```

**Parameters:**
- `message: Message | None` — The message object.

**Returns:** `int | None`
</details>


# Context Manager

<details>
<summary>Normal Usage</summary>

This form **does not automatically send** the message.  
It only groups your setter calls in a clean block:

```python
with self.chain.sender as sender:
    sender.set_title("😃 Welcome!")
    sender.set_message("It's Telekit.")
```

You still need to call `self.chain.send()` afterward.

</details>

<details>
<summary>then_send()</summary>

If you want the message to be sent automatically at the end of the block, use:

```python
with self.chain.sender.then_send() as sender:
    sender.set_title("Hello!")
    sender.set_message("This message is sent automatically on exit.")
```

> [!IMPORTANT] 
> `then_send()` calls the sender’s own `send()` method, *not* `chain.send()`.  
> Because of this, features that rely on `chain.send()` — such as `inline_keyboard` — will **not** be processed when using this mode.

</details>

[Next: Styles »](6_styles.md)