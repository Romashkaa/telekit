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

- New `entry_document` decorator!
- New `entry_text_document` decorator!