## Obsidian Canvas Mode *(Beta)*
Build bots visually — no DSL required. Design your dialog flow as a flowchart in Obsidian and connect it to Telekit with a single method call.

- Added `analyze_canvas()` to `DSLHandler` — loads a `.canvas` file as an executable model

## Styles Improvements
The style system has been rewritten from the ground up. Previously, automatic escaping was quite unpredictable — users couldn't always tell when a string would be escaped or not. That's over.

- Migrated markdown rendering to **MarkdownV2**
- Added `Stack` style for structured list rendering
- Added `Mention` style
- Renamed `Sanitize` to `Escape`
- Renamed `NoSanitize` to `Raw`
- Added `utils.sanitize_markdown()` — escapes all MarkdownV2 special characters outside valid entities
- Added `utils.adapt_markdown()` — converts `**bold**` / `*italic*` to Telegram-compatible format
- Added `utils.telegramify_markdown()` — convenience pipeline: adapt + sanitize
- `StyleFormatter` renamed to `TextEntity`

## Inline Keyboards

Inline keyboards got a proper type system. Previously, any string value in the keyboard dict was treated as a link. Now every button type is explicit.

- Introduced `InlineButton` base class with subclasses:
  `LinkButton`, `WebAppButton`, `SuggestButton`, `CopyTextButton`, `CallbackButton`
- `CallbackButton` — pass arguments to callbacks and set visual style
- Added `ButtonStyle` enum — style your inline buttons (Bot API 9.4)
- Added `inline_choice` / `set_inline_choice` methods
- `set_entry_suggestions` now warns when Telegram Bot API limits are exceeded
- It's no longer pass `Message` object to callbacks
- Reduced closure size and improved callback performance

## Chain Improvements
- Added `set_break_only_on_match()` — control whether chain interrupts only on valid handler match, not random input
- Added `set_break_on_commands()` — control whether commands take priority over entry handlers
- Improved file extension validation via **pathlib**
- `entry_*` handlers no longer pass `Message` by default — use `include_message=True` to restore

## CallbackQueryHandler
- Callbacks now invoked directly — no virtual message conversion, faster response times
- Native alert support for expired or inactive buttons
- Added `set_invalid_data_answer()` and `set_button_is_no_active_answer()` for global customization

## DSL Improvements
- `jinja_env` is now private — use `get_jinja_env()` instead
- `TelekitDSL` class:
  - All `from_*` factory methods now use `type()` for class creation

## Fixes
- Fixed one-time trigger bug — triggers like `on.text` now fire reliably across multiple messages while a chain timeout is active

## Other
- Added `utils.read_token()` and `utils.read_canvas_path()` — clean helpers for reading credentials from files
- Added `utils.format_file_size()`
- Added `set_license_text` to senders
- Added `format_size` to `TextDocument`
- Added `TelekitState` class
- Bumped `pyTelegramBotAPI` to **v4.31.0**
- Added GPL v3 License

## 🚀 Upcoming

- New triggers: `document`, `text_document`
- Telekit DSL: shorter notation and button attributes with style, alert, ... support