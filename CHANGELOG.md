### v2.5.1 `(bug-fix)`
- Implement `TelegramMarkdownV2Sanitizer` for improved `MarkdownV2` handling

### v2.5.0 `(final)`
- Refactor `CalendarPick` trait to use `set_keyboard`

### v2.5.0`b3`
- Added `utils.Markers` class
- Added `HTMLText` class for handling Telegram HTML strings with tag-aware indexing and slicing.
- Added `PaginatedText` trait for displaying long HTML text in a paginated format, supporting navigation and smart splitting.
- Added `__radd__` to `TextEntity`: `"Regular" + Bold(" and Bold")`
- Added `__mul__` to `TextEntity`: `Bold("Text") * 3`
- Added `enabled=` parameter to `TextEntity`: `Bold("bold text", enabled=is_text_bold)`
- Added `TextBuilder` class – a fluent message composition API mirroring `InlineKeyboard`'s builder pattern
- Added styles to `telekit.types`
- Added `utils.CyclicList`
- Fixed `_answer_callback_query` to always call `bot.answer_callback_query()`, even without a popup text

### v2.5.0`b2`
- Added the `escape` parameter to `telekit.utils.*`:
  - `make_user_link`
  - `make_bot_link`
- `Handler.handlers_dict` now excludes private handlers (classes whose names start with `_`).
- Added `Debug.duplicate_handler_warnings` to warn about duplicate handler names during initialization.
- Added `Handler.chat` object (BETA)

### v2.5.0`b1`
- Added `Sender.send_message` method.
- Added `utils.make_mention` utility for generating `tg://user?id=` mention links.
- Added new inline button types to `inline_buttons`:
  - `ContactButton` — mentions a user by Telegram ID via `tg://user?id=`.
  - `UserLinkButton` — opens a user profile by username; supports pre-filled message text.
  - `BotLinkButton` — opens a bot by username; supports deep-link `?start=` payload.
- Added new methods to `InlineKeyboard`:
  - `add_contact` — adds a `ContactButton`.
  - `add_user_link` — adds a `UserLinkButton`.
  - `add_bot_link` — adds a `BotLinkButton`.

### v2.5.0`b0`
- Added support for t-strings (PEP 750, Python 3.14+) in `TextEntity`.