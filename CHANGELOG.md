## Chain Improvements
- Improved file extension validation in  
  `set_entry_text_document`, `entry_text_document`, `entry_document`, and `set_entry_document`.  
  Validation is now performed using **pathlib**.

- All `entry_*` and `set_entry_*` handlers **no longer pass the `Message` object to the callback by default**.  
  A new `include_message` parameter was added to restore the previous behavior when needed.

- Introduced a new `InlineButton` base class.
  Its subclasses - `LinkButton`, `WebAppButton`, `SuggestButton`, `CopyTextButton`, `CallbackButton` provide support for special inline buttons such as:
  - external links
  - web apps
  - suggestions  
  - text copying  
  - callbacks with additional parameters
  These can now be passed as dictionary values in `set_inline_keyboard` and related methods.

- Reduced closure size and improved performance for each callback button.

- Added new inline keyboard methods:  
  `inline_choice` and `set_inline_choice`.

- `set_entry_suggestions` now warns when **Telegram Bot API limits** are exceeded.

## More Configuration

- **New Toggle `chain.set_break_only_on_match()`:** Added a mechanism to decide whether the current `Chain` should be interrupted by messages that don't match any global handlers.
  - **Behavior (Default: Enabled):** 
    - **Enabled:** The `Chain` is interrupted only if the incoming message triggers another existing handler (e.g., `on.text` or a command). Random messages that don't match any triggers are ignored, keeping the process active.
    -  **Disabled:** Any incoming message will immediately terminate the current `Chain`, even if it matches no other logic in the bot.
  -  **Purpose:** Ensures that accidental user input doesn't break a multi-step flow unless a valid alternative action is triggered.
- **New Toggle `chain.set_break_on_commands()`:** Sets whether commands (messages starting with '/') should take priority over the current entry handler. 
  - If `True`, commands will always terminate the chain and trigger the corresponding command handler. 
  - If `False`, commands will be passed to the entry handler like regular text

## DSL Improvements
- **Mixin update:** the `jinja_env` attribute is now private.
- Added a new method: `get_jinja_env`.
- In `TelekitDSL`, all `from_*` factory methods now create classes using `type()`
  instead of standard class definitions.

## Handler Improvements
- Add new trigger:
    - `func`
- Improved `handoff` type hints (using `@overload`)

## CallbackQueryHandler Improvements

- **Alert Support for Callback Answers:** Added native support for `alert` responses in `callback_query`. If a button is expired or inactive, a modal alert will now be displayed. Additionally, when using `CallbackButton`, you can specify a custom `answer_text` to be shown as an alert upon clicking.
- **Customizable Response Methods:** Introduced `set_invalid_data_answer` and `set_button_is_no_active_answer` methods. These allow developers to globally customize the text and display type (alert vs. notification) for invalid data or deactivated buttons.
- **Direct Callback Execution:** Optimized the interaction logic. Previously, all button clicks were converted into virtual messages processed by the current Chain's `InputHandler`. Now, the `CallbackQueryHandler` stores button callbacks internally and invokes them directly, ensuring faster response times.

## Fixed Bugs
- Fixed a bug that caused `text`, `photo`, and similar handlers to behave as “one-time” triggers. Previously, while an active chain was waiting for its `timeout`, all incoming messages were only checked for commands. Only a command could interrupt the current chain — any other messages were ignored. As a result, triggers (for example, on the message `"hello"`) could effectively fire only once. This behavior has now been corrected: new messages are processed properly, and triggers work reliably without a one-time limitation.

## Planned:
- Add new triggers:
    - document
    - text_document
- Telekit DSL syntax:
  - Shorter notation
```go
@ main {
  button next()
}
```
  - Attributes
```go
@ main {
  buttons {
    handoff("Start", "StartHandler").invoke("start_script", ["args"])
    cancel("✕ Cancel").notify("Canceled...").style("danger") // "style" – Bot API 9.4 (February 9, 2026)
    next("✓ Okay").alert("Pressed; Click 'OK'").style("success")
  }
}
```