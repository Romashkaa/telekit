# 0.0.2

1. Snapvault and Chapters packages were not loading. (BUG)

# 0.0.3

1. Documentation update (README.md).
2. Improved inline documentation within the library.
3. `Handler` now automatically calls `self.get_chain()` during initialization.
4. Other fixes and preparation for release.

# 0.0.4

1. New `@Handler.on_text()` decorator – example available in `telekit/example/example_handlers/on_text.py`!

# 0.0.8

1. `inline_keyboard` and `entry`s no longer conflict
2. New `entry_photo` decorator!

# 0.0.9 and 0.0.10

- 0.0.9. Refactor imports and remove commented-out code
- 0.0.10. Add delete_user_initial_message method to remove user's initial message

# 0.0.11

1. The message parameter for functions used in set_inline_keyboard is now optional. Handlers can be defined without requiring a message object.
2. Refactor Parser class to accept data directly and improve error handling in read function

# 0.0.12 (unreleased)
## New Features:
### New decorators
- Added `entry_document` decorator.
```python
@self.chain.entry_document(allowed_extensions=(".zip",))
def doc_handler(message: telebot.types.Message, document: telebot.types.Document):
    print(document.file_name, document)
```
- Added `entry_text_document` decorator.
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
### Logging functionality
- Introduced a new `logger` module to handle logging for the library and individual users.
- Implemented full logging functionality across the Telekit library.
- Integrated logging into key components, including handlers, senders, and the server.
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
## Improvements:
- Updated error handling to log exceptions with appropriate severity levels.
- Typing improvements: New class `telekit.types`
