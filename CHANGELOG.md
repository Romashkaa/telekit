# 0.2.0
## New Features
- `Server` now accepts a **bot token string** directly:
You can initialize the server either with an existing `TeleBot` instance or with a token string:

```python
import telekit

server = telekit.Server("BOT_TOKEN")
server.polling()
```

If a string is provided, a `TeleBot` instance is created internally automatically. 
- `telekit.GuideMixin` and `telekit.GuideKit(...).register()`: allows creating interactive FAQ pages using a custom DSL, with automatic scene handling, user input processing, and message formatting.
- `Styles` helper class: easily create styled text objects (`Bold`, `Italic`, `Underline`, `Strikethrough`, `Code`, `Python`, `Spoiler`, `Quote`) with automatic `parse_mode` support for Markdown or HTML.
- `@chain.entry_location()` decorator: allows handling messages with user coordinates.
- `@chain.on_timeout()` decorator: registers a callback to be executed after a timeout.  
- `chain.set_timeout()` an alternative way to set a timeout programmatically.
- `server.long_polling()` an alternative to `server.polling()` that uses long polling with a configurable timeout

## Deprecation Notice
- Handlers that use the old signature `init_handler(cls, bot)` are now **deprecated**. A warning will be shown in logs when such handlers are initialized. This method will be **removed completely in the next major release**. Use `cls.bot` directly or switch to Telekit’s built-in handler methods (e.g. `cls.handle_message(...)`).

## Planned:
- Result caching in `GuideKit`
- Ability to disable logging `server.enable_logging(True)`
- Localization of the method effect `self.user.enable_logging()` (Currently working globally)

---

# 0.1.1
## Bug Fixes:
- Fixed an issue where `@self.chain.entry_text(delete_user_response=True)` would delete the bot’s message if `set_entry_suggestions` was used.

---

# 0.1.0
## New Features:
### Handler Methods

- Added `simulate_user_message` method to programmatically simulate user messages. Useful for testing handlers or switching between commands without sending real Telegram messages:
```python
self.simulate_user_message("/start")
```

### New Decorators

- Added `entry_document` decorator:

```python
@self.chain.entry_document(allowed_extensions=(".zip",))
def doc_handler(message: telebot.types.Message, document: telebot.types.Document):
    print(document.file_name, document)
```

- Added `entry_text_document` decorator:

```python
@self.chain.entry_text_document(allowed_extensions=(".txt", ".js"))
def text_document_handler(message: telebot.types.Message, text_document: telekit.types.TextDocument):
    print(
        text_document.text, 
        text_document.file_name,
        text_document.encoding, 
        text_document.document
    )
```

### Logging Functionality
- Introduced a new `logger` module to handle logging for the library and individual users.
- Implemented full logging functionality across the Telekit library.
- Integrated logging into key components, including handlers, senders, and the server.
```log
2025-11-08 17:20:37 | WARNING | senders.py | Failed to delete message 521. Maybe the user deleted it. Exception: A request to the Telegram API was unsuccessful. Error code: 400. Description: Bad Request: message to delete not found
2025-11-08 17:20:37 | WARNING | senders.py | Failed to edit message 521, sending new one instead. Exception: A request to the Telegram API was unsuccessful. Error code: 400. Description: Bad Request: message to edit not found
```
- Added methods to enable user-specific logging in the `User` class:
```python
# help.py [self = HelpHandler()]; [HelpHandler.handle(self)]:
# Call `self.user.enable_logging(1914626823, ...)` to enable logging for specific users.
self.user.enable_logging(1914626823)
self.user.logger.info(f"You (admin) clicked: {value[0]}")

# If no `chat_id`s are provided, logging is enabled for the current user (`self.user.chat_id`).
self.user.enable_logging()
self.user.logger.info(f"User clicked: {value[0]}")
```
```log
2025-11-08 17:20:43 | INFO | help.py:61 | [IDIDIDIDID] User clicked: Another Page
```

### Other Improvements:

- Updated error handling to log exceptions with appropriate severity levels.
- Typing improvements: New class `telekit.types`

## Bug Fixes:

- #1 Fixed! The main Telekit issue — **Double Handling**:
  Previously, if a user sent two or more commands to the bot while it was offline, the bot would process all of them **concurrently** after restarting.  
  This behavior could cause unexpected results and race conditions.  

---

# 0.0.11

1. The message parameter for functions used in set_inline_keyboard is now optional. Handlers can be defined without requiring a message object.
2. Refactor Parser class to accept data directly and improve error handling in read function

# 0.0.10

- Add delete_user_initial_message method to remove user's initial message

# 0.0.9

- Refactor imports and remove commented-out code

# 0.0.8

1. `inline_keyboard` and `entry`s no longer conflict
2. New `entry_photo` decorator!

# 0.0.4

1. New `@Handler.on_text()` decorator – example available in `telekit/example/example_handlers/on_text.py`!

# 0.0.3

1. Documentation update (README.md).
2. Improved inline documentation within the library.
3. `Handler` now automatically calls `self.get_chain()` during initialization.
4. Other fixes and preparation for release.

# 0.0.2

1. Snapvault and Chapters packages were not loading. (BUG)

# 0.0.1

- Published