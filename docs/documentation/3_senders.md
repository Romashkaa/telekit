# Senders

Senders in Telekit provide a high-level interface for sending and managing messages in Telegram bots. They wrap the standard TeleBot API, adding convenience features such as temporary messages, automatic editing, error handling, formatting, adding photos and effects.

## Basic 

You use `self.chain.sender.*` to define how your bot responds.

- `set_message_effect_id(effect: str)` - Sets the message effect by string ID.  
- `set_effect(effect: BaseSender.Effect | str | int)` - Sets a message effect using enum, string, or integer.  
- `Effect` - Enum representing message effects:
    - `FIRE` - 🔥  (`"5104841245755180586"`)
    - `PARTY` - 🎉 (`"5046509860389126442"`)
    - `HEART` - ❤️ (`"5159385139981059251"`)
    - `THUMBS_UP` - 👍 (`"5107584321108051014"`)
    - `THUMBS_DOWN` - 👎 (`"5104858069142078462"`)
    - `POOP` - 💩 (`"5046589136895476101"`)
- `set_photo(photo: str | None | Any)` - Sets the photo for the message. Accepts:
    - URL string (`"http://..."` or `"https://..."`)
    - local file path
    - bytes or file-like object
    - `None` to remove any previously set photo
- `set_media(*media: str | Any)` - Sets multiple media items. Accepts:
    - URLs
    - local file paths
    - bytes or file-like objects
    - instances of `InputMediaPhoto`
- `set_chat_id(chat_id: int)` - Sets the chat ID for sending messages.  
- `set_text(text: str)` - Sets the plain text of the message.  
- `set_reply_markup(reply_markup)` - Inline keyboards, reply keyboards, or other markup objects.  
- `set_temporary(is_temp: bool)` - Marks message as temporary; will be deleted later if `delete_temporaries` is True.  
- `set_delete_temporaries(del_temps: bool)` - Whether to automatically delete temporary messages in the chat.  
- `set_parse_mode(parse_mode: str | None)` - `"html"`, `"markdown"` or `None`.  
- `set_reply_to_message_id(reply_to_message_id: int | None)` - Reply to specific message by ID.  
- `set_edit_message_id(edit_message_id: int | None)` - Edit an existing message by ID.  
- `set_edit_message(edit_message: Message | None)` - Edit a specific `Message` object.  
- `set_reply_to(reply_to: Message | None)` - Reply to a specific `Message` object.  
- `delete_message(message: Message | None, only_user_messages: bool=False) -> bool` - Deletes a message optionally ignoring bot messages.  
- `pyerror(exception: BaseException) -> Message | None` - Sends a Python exception as a message.  
- `error(title: str | StyleFormatter, message: str | StyleFormatter) -> Message | None` - Sends a custom error message.  
- `try_send() -> tuple[Message | None, Exception | None]` - Attempts to send a message with error handling.  
- `send_or_handle_error() -> Message | None` - Sends a message and handles errors if they occur.  
- `send() -> Message | None` - Sends or edits a message, managing temporary state.  
- `get_message_id(message: Message | None) -> int | None` - Retrieves the message ID from a Message object.  

## Alert Sender

AlertSender is a special sender that sends a message and automatically formats its style (title, message body, italics, etc.).

- `set_text(text: str | StyleFormatter)` - Sets the full text of the alert, clears title and message.  
- `set_title(title: str | StyleFormatter)` - Sets the alert title, clears text and message.  
- `set_message(*message: str | StyleFormatter, sep: str | StyleFormatter="")` - Sets the alert message body, clearing text.  
- `add_message(*message: str | StyleFormatter, sep: str | StyleFormatter="")` - Appends to the alert message body.  
- `set_parse_mode(parse_mode: str | None=None)` - Sets the parse mode for the alert message.  
- `set_use_italics(use_italics: bool=True)` - Sets whether to use italics in the message.  
- `set_use_newline(_use_newline: bool=True)` - Sets whether to add a newline between title and message.  
- `send() -> Message | None` - Compiles and sends the alert message.  

## Under-the-Hood Methods

These settings are handled automatically, but you can override them if needed:

- `set_chat_id(chat_id)`: Change target chat.
- `set_edit_message(message)`: Set the message to edit.
- `set_reply_markup(reply_markup)`: Add inline/keyboard markup. Raw.

---

- [See tutorial](../tutorial/3_senders.md)
- [Next: Text Styling »](4_text_styling.md)