# Examples

This section contains small, focused example projects built with Telekit.

Examples are intentionally minimal: you can copy them, modify them, or use them as a starting point for your own bots.

> Use Command ⌘ + F to quickly find a specific method, attribute, or parameter.

## Basic

| Name  | Comment | Used methods |
|-----------|--------------|-------------------------|
| [Dialogue](dialogue.md)   | Simple text-based dialogue flow | `on.text`, `entry_text` |
| [Risk Game](risk_game.md) | Interactive game | `inline_keyboard`, `set_remove_inline_keyboard`, `set_remove_timeout`, `set_default_timeout`, `on.command` |
| [Counter](counter.md) | Counter with buttons "+" and "-" | `set_photo`, `set_effect`, `inline_keyboard`, `set_remove_inline_keyboard` |
| [On Text](on_text.md) | Example of handling specific templated messages | `on.text`, `styles`, `user`, `username`, `Code` |
| [Append](append_method.md) | Appending messages with timeout control | `append`, `styles`, `set_timeout`, `set_use_italics`, `Sanitize` |
| [Ads](ads.md) | Sending messages to several chats | `on.command`, `whitelist=`, `create_sender`, `send_or_handle_error`, `set_effect` |
| [Redirect](redirect.md) | Message with buttons linking to other handlers | `handoff`, `on.command`,  `inline_keyboard`, `user`, `first_name` |
| [Deep Linking: Command Parameters & Invite Code](command_parameters.md) | Example of handling `/start <age> <name>` commands with type-checked parameters | `parameters`, `params=`, `set_parse_mode`, `set_text`, `Sanitize`, `set_reply_to`, `message` |

## Telekit DSL

| Name | Comment | Used methods |
|-----------|--------------|-------------------------|
| [FAQ](faq.md) | FAQ generation from string | `analyze_source`, `from_string` |
| [Quiz](quiz.md) | Example of DSL code | `analyze_source`, `start_script` |
| [Custom Variables](custom_variables.md) | Example of custom variables in the script | `get_variable`, `analyze_source` |
| [Python API](python_api.md) | Example of calling Handler methods directly from a script | `on_enter`, `get_variable`, `analyze_source`, `start_script` |

## Complex

| Name | Comment | Used methods |
|-----------|--------------|-------------------------|
| [Registration](registration.md) | Simple registration example | `Vault`, `entry_text`, `set_entry_suggestions`, `set_inline_keyboard` |

If you're unsure how the examples work, [check out our tutorial](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/0_tutorial.md) for a full walkthrough.