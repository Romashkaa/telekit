### v2.5.0`b0`
- Added support for t-strings (PEP 750, Python 3.14+) in `TextEntity`.

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

### v2.5.0`b2`
- Added the `escape` parameter to `telekit.utils.*`:
  - `make_user_link`
  - `make_bot_link`
- `Handler.handlers_dict` now excludes private handlers (classes whose names start with `_`).
- Added `Debug.duplicate_handler_warnings` to warn about duplicate handler names during initialization.
- Added `Handler.chat` object (BETA)