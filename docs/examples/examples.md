# Examples

This section contains small, focused example projects built with Telekit.

Examples are intentionally minimal: you can copy them, modify them, or use them as a starting point for your own bots.

## Basic

| Name | Comment | Used methods |
|------|---------|-------------------------|
| [Dialogue](dialogue.md)   | Simple text-based dialogue flow | `on.text`, `entry_text` |
| [Risk Game](risk_game.md) | Interactive game | `inline_keyboard`, `set_remove_inline_keyboard`, `set_remove_timeout`, `set_default_timeout` |
| [Counter](counter.md) | Counter with buttons "+" and "-" | `set_photo`, `set_effect` |
| [On Text](on_text.md) | Example of handling specific templated messages | `on.text`, `styles` |
| [Append](append_method.md) | Appending messages with timeout control | `append`, `styles`, `set_timeout` |
| [Ads](ads.md) | Sending messages to several chats | `whitelist`, `create_sender`, `send_or_handle_error`, `set_effect` |

## Telekit DSL

| Name | Comment | Used methods |
|------|---------|--------------|
| [FAQ](faq.md) | FAQ generation from string | `analyze_source`, `from_string` |
| [Quiz](quiz.md) | Example of DSL code | `analyze_source` |

## Complex

| Name | Comment | Used methods |
|------|---------|--------------|
| [Registration](registration.md) | Simple registration example | `Vault`, `entry_text`, `set_entry_suggestions` |


## Contents

- Basic:
    - [Dialogue](dialogue.md) – on.text, entry_text.
    - [Risk Game](risk_game.md) – inline_keyboard, set_remove_inline_keyboard, set_remove_timeout, set_default_timeout.
    - [Counter](counter.md) – set_photo, set_effect.
    - [On Text](on_text.md) – on.text, styles.
    - [Append](append_method.md) - append, styles, set_timeout.
    - [Ads](ads.md) - whitelist, create_sender, send_or_handle_error, set_effect.
- Telekit DSL:
    - [FAQ](faq.md) – analyze_source, from_string.
    - [Quiz](quiz.md) – telekit dsl syntax.
- Complex:
    - [Registration](registration.md) – Vault, entry_text, set_entry_suggestions.

If you're unsure how the examples work, [check out our tutorial](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/0_tutorial.md) for a full walkthrough.