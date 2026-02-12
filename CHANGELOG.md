## Chain Improvements
- Improved file extension validation in  
  `set_entry_text_document`, `entry_text_document`, `entry_document`, and `set_entry_document`.  
  Validation is now performed using **pathlib**.

- All `entry_*` and `set_entry_*` handlers **no longer pass the `Message` object to the callback by default**.  
  A new `include_message` parameter was added to restore the previous behavior when needed.

- Introduced a new `InlineButton` base class.
  Its subclasses - `LinkButton`, `WebAppButton`, `SuggestButton`, and `CopyTextButton` provide support for special inline buttons such as:
  - external links
  - web apps  
  - suggestions  
  - text copying  
  These can now be passed as dictionary values in `set_inline_keyboard` and related methods.

- Reduced closure size and improved performance for each callback button.

- Added new inline keyboard methods:  
  `inline_choice` and `set_inline_choice`.

- `set_entry_suggestions` now warns when **Telegram Bot API limits** are exceeded.

## DSL Improvements
- **Mixin update:** the `jinja_env` attribute is now private.
- Added a new method: `get_jinja_env`.
- In `TelekitDSL`, all `from_*` factory methods now create classes using `type()`
  instead of standard class definitions.

## Handler Improvements
- Add new trigger:
    - `func`

## Fixed Bugs
- Fixed a bug that caused `text`, `photo`, and similar handlers to behave as “one-time” triggers. Previously, while an active chain was waiting for its `timeout`, all incoming messages were only checked for commands. Only a command could interrupt the current chain — any other messages were ignored. As a result, triggers (for example, on the message `"hello"`) could effectively fire only once. This behavior has now been corrected: new messages are processed properly, and triggers work reliably without a one-time limitation.

## Planned:
- Add new triggers:
    - document
    - text_document