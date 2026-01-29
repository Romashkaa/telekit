# Senders

Senders in Telekit provide a high-level interface for sending and managing messages in Telegram bots. They wrap the standard TeleBot API, adding convenience features such as temporary messages, automatic editing, error handling, formatting, adding photos and effects.

## Send Text Messages

There are two main ways to create a message: a simple text message or a structured message with a title and body:

<details><summary>Plain Text Message</summary>

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

<details><summary>Message with a Title and Body</summary>

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

<details><summary>Append Additional Text</summary>

Append additional text to the current message content:

```py
self.chain.sender.set_text("Hello")
self.chain.sender.append(", how are you?")
self.chain.sender.append(" Fine?")
self.chain.send()
```

> Useful for building messages in a for-loop.
</details>

<details><summary>set_parse_mode</summary>

Set the parse mode for message formatting (e.g., Markdown, HTML):

```py
self.chain.sender.set_parse_mode("markdown")
self.chain.sender.set_text("*Bold text* and _italic text_.")
self.chain.send()
```

You can also use constants:

```py
from telekit.types import ParseMode
self.chain.sender.set_parse_mode(ParseMode.HTML)
```

> Choose the appropriate parse mode for your formatting needs.

</details>

## Attach Media to Messages

<details><summary>Photos</summary>

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

<details><summary>Documents</summary>

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

<details><summary>Videos</summary>

Attach a video file using `set_video()` before sending:

```py
self.chain.sender.set_video("cats.mp4")
self.chain.sender.set_text("Watch this video!")
self.chain.send()
```

> Supported sources are local paths, URLs, or Telegram file IDs.

</details>

<details><summary>Video Notes</summary>

Send circular video notes with `set_video_note()`:

```py
self.chain.sender.set_video_note("video_note.mp4")
self.chain.send()
```

> Video notes are short, round videos.

</details>

<details><summary>Animation</summary>

Send GIF animations using `set_animation()`:

```py
self.chain.sender.set_animation("funny.gif")
self.chain.send()
```

> Animations support the same sources as photos and videos.

</details>

<details><summary>Audio</summary>

Attach audio files with `set_audio()`:

```py
self.chain.sender.set_audio("Romashka - R2 (CDs).mp3")
self.chain.send()
```

> Useful for sending music or sound clips.

</details>

<details><summary>Voice</summary>

Send voice messages using `set_voice()`:

```py
self.chain.sender.set_voice("voice.ogg")
self.chain.send()
```

> Voice messages are short audio clips recorded by the user.

</details>

<details><summary>Media Groups</summary>

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

<details><summary>Removing Attachments</summary>

Remove any attached media or documents before sending with `remove_attachments()`:

```py
self.chain.sender.set_photo("photo.jpg")
self.chain.sender.remove_attachments()  # clears photo
self.chain.sender.set_text("There's no photo ;)")
self.chain.send()
```

> Useful when you want to clear previous attachments.

</details>

## Message Control

<details><summary>set_reply_to</summary>

Make the message a reply to another message object:

```py
self.chain.sender.set_reply_to(self.message) # reply to the user's initial message
self.chain.sender.set_text("Replying to your message.")
self.chain.send()
```

> Replies help maintain conversation context.

</details>

<details><summary>set_reply_to_message_id</summary>

Reply by specifying the message ID directly:

```py
self.chain.sender.set_reply_to_message_id(self.message.message_id) # reply to the user's initial message
self.chain.sender.set_text("Reply by message ID.")
self.chain.send()
```

> Use when you only have the message ID.

</details>

<details><summary>set_edit_message</summary>

Edit an existing message object instead of sending a new one:

```py
self.chain.sender.set_edit_message(message)
self.chain.sender.set_text("Edited message content.")
self.chain.send()
```

> Edits modify the content of an existing message.

</details>

<details><summary>set_edit_message_id</summary>

Edit a message by specifying its ID:

```py
self.chain.sender.set_edit_message_id(message.message_id)
self.chain.sender.set_text("Edit by message ID.")
self.chain.send()
```

> Useful when you only know the message ID.

</details>

<details><summary>set_chat_id</summary>

Specify the chat ID to send or edit the message in:

```py
self.chain.sender.set_chat_id(472584)
self.chain.sender.set_text("Message to specific chat.")
self.chain.send()
```

> Overrides the default chat ID (self.message.chat.id).

</details>

## Effects

<details><summary>set_effect</summary>

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

<details><summary>set_message_effect_id</summary>

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

<details><summary>set_temporary</summary>

Mark the current message as temporary. It will be deleted later if `set_delete_temporaries(True)` is enabled:

```py
self.chain.sender.set_temporary(True)
self.chain.sender.set_text("This message will be temporary.")
self.chain.send()
```

> [!IMPORTANT] 
> Only flags the message as temporary; deletion happens during sending next message.

</details>

<details><summary>set_delete_temporaries</summary>

Enable deletion of previously marked temporary messages in the current chat:

```py
self.chain.sender.set_delete_temporaries(True) # `True` by default
self.chain.sender.set_text("This message triggers deletion of previous temporary messages.")
self.chain.send()
```

> Deletion of previous temporary messages occurs when sending the current message.

> [!IMPORTANT] 
> - `set_temporary()` only marks the current message.  
> - `set_delete_temporaries()` only triggers deletion of earlier temporary messages.

</details>

## Sending & Error Handling

<details><summary>send</summary>

Send the prepared message:

```py
self.chain.sender.send()
```

> Sends or edits the message, including management of temporary messages. Does **not** handle exceptions — any error will be raised.

> [!IMPORTANT]
> `self.chain.sender.send()` only sends the message itself. It does not handle inline keyboards or other interactions — for those, you should use `self.chain.send()` or `self.chain.edit()`!

</details>

<details><summary>try_send</summary>

Attempt to send the message, returning message OR exception:

```py
message, error = self.chain.sender.try_send()

if message:
    print(f"Message #{message.message_id} was sent")
else:
    print(f"Exception: {error}")
```

> Attempts to send the message with error handling. 

Returns: 
- `[Message, None]` on success
- `[None, Exception]` on failure

</details>

<details><summary>send_or_handle_error</summary>

Attempts to send the message with error handling. Returns `Message` if the message was sent successfully, or `None` if an error occurred:

```py
message: Message | None = self.chain.sender.send_or_handle_error()

if message:
    print(f"Message #{message.message_id} was sent successfully")
```

If an error occurs, an error message containing the **exception type and description** is automatically sent to the user:

```md
**ApiTelegramException**

_A request to the Telegram API was unsuccessful. Error code: 400. Description: Bad Request: can't parse entities: Can't find end tag corresponding to start tag "b"._
```

> [!IMPORTANT]
> `self.chain.sender.send_or_handle_error()` only sends the message itself. It does not handle inline keyboards or other interactions — for those, you should use `self.chain.send()` or `self.chain.edit()`!


</details>

## Action Methods

These methods do not configure the current message; instead, they perform a specific action immediately.

<details><summary>send_chat_action</summary>

Send chat actions like typing indicators:

```py
from telekit.types import ChatAction

self.chain.sender.send_chat_action(ChatAction.TYPING)
```

> Shows the bot is performing an action.

</details>

<details>
<summary>delete_message</summary>

Deletes a message, optionally ignoring bot messages.

```py
self.chain.sender.delete_message(message, only_user_messages=False)
```

**Parameters:**
- `message: Message | None` — The message to delete.
- `only_user_messages: bool` — If True, only deletes user messages.
</details>

<details>
<summary>pyerror</summary>

Sends a Python exception as a message.

```py
try:
    ...
except Exception as exception:
    self.chain.sender.pyerror(exception)
```

</details>

<details>
<summary>error</summary>

Sends a custom error message.

```py
self.chain.sender.error("Error Heading", "Something went wrong...")
```

**Parameters:**
- `title: str | StyleFormatter` — The title of the error.
- `message: str | StyleFormatter` — The error message body.
</details>

<details>
<summary>get_message_id</summary>

Retrieves the message ID from a Message object.

```py
msg_id = self.chain.sender.get_message_id(message)
```

**Parameters:**
- `message: Message | None` — The message object.
**Returns:** `int | None`
</details>


# Context Manager

<details><summary>Normal Usage</summary>

This form **does not automatically send** the message.  
It only groups your setter calls in a clean block:

```python
with self.chain.sender as sender:
    sender.set_title("😃 Welcome!")
    sender.set_message("It's Telekit.")
```

You still need to call `self.chain.send()` afterward.

</details>

<details><summary>then_send()</summary>

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