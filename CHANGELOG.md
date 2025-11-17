# 1.0.0 BETA

Version that introduced a new trigger-handling logic. Reduced confusion and minimized the risk of bugs caused by developer oversight. Workarounds for handling Chain—which could theoretically create recursion when searching for a parent—have been removed.

## New Features
- The new `on` API provides a cleaner and more intuitive way to declare triggers for messages and commands:

```python
@cls.on.command('start')
def start_handler(message):
    cls(message).handle_start()

@cls.on.text("My name is {name}")
def name_handler(message, name: str):
    cls(message).handle_name(name)

# A simpler ways (Automatic instance creation `cls(message)`):

cls.on.command("start").invoke(cls.handle_start)
cls.on.text("My name is {name}").invoke(cls.handle_name)
```
- Sender:
    - **Automatic HTML and Markdown handling** – the library now automatically processes HTML tags and Markdown formatting when they are applied via constructs such as `styles.Bold(...)` or within specialized blocks like `styles.Sanitize(...)`.
    - **Enhanced Sender logic** – the Sender now automatically sanitizes Markdown and HTML content within the aforementioned style blocks, and automatically assigns the appropriate `parse_mode` to these blocks, ensuring safe and consistent message formatting.
    - New `sender.set_media(...)` method.
    - New `chain.create_sender(chat_id)` method.
- New `telekit.enable_file_logging()` function.
- New `handler.new_chain() -> None` method.
- New `TelekitDSL.from_file(...)` and `TelekitDSL.from_string(...)` methods for creation handlers with Telekit DSL.
- Renamed `GuideMixin`, now `TelekitDSL.Mixin`.
- Telekit DSL: 
    - Added three types `none`, `true`, and `false` — accepted in any letter case (NONE, True, fAlSe, etc.).
    - Parser prevents creation of scenes with reserved name `back`.
    - New syntax:
        - new `row_width` syntax: `buttons[2]` -> `buttons(2)`.
        - new “buttons without label” behavior. [See details](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#buttons-without-label).
    - New Telekit DSL Documentation.
- New `chain.remove_all_handlers()` method. Forces removal of all callback handlers associated with the chain.
    - New `chain.remove_timeout()` — removes active timeout handler.
    - New `chain.remove_entry_handler()` — removes the current entry handler.
    - New `chain.remove_inline_keyboard()` — removes the inline keyboard and all callback bindings.
    - By default, all of them are automatically called after `chain.send()` or `.edit()`, but you can disable this behavior:
        - `chain.set_remove_timeout(False)`
        - `chain.set_remove_entry_handler(False)`
        - `chain.set_remove_inline_keyboard(False)`
- New tutorial ([Tutorial](docs/tutorial/0_tutorial.md))
- Other.

## Breaking Changes
- renamed `GuideKit` and `GuideMixin`
    - now `TelekitDSL` and `TelekitDSL.Mixin`
- changed `GuideKit(...)`.
    - now `TelekitDSL.from_file(...)`
- removed `chain.set_always_edit_previous_message(...)` method.
- removed `chain.parent` and everything related to it.
- removed `handler.get_child()` method.
- removed `handler.get_chain(...)` method.
    - now `handler.new_chain() -> None` method.
- renamed `chain.edit_previous_message()` for better clarity:
    - now `chain.mark_previous_message_for_edit()` method.
- changed default `parse_mode` value in DSL:
    - now `none`
- changed `buttons[2]` -> `buttons(2)` - DSL

## Delayed until v1.1.0
- Display a warning in the DSL when a string contains too many buttons or excessive text.
- Support localization for the effect of the `self.user.enable_logging()` method (currently applied globally).

---

Old release notes are available in previous commits.