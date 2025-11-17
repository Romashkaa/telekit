# 1.0.0 (BETA 3)

**Overview:**  
This release makes creating triggers simpler, styling messages easier, and the DSL smarter. We removed tricky `Chain` workarounds that could cause unexpected behavior, improved automatic handling of HTML and Markdown in messages, and added powerful new styles. Everything is now safer, cleaner, and more intuitive for developers.

## ✅ New Features
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

### Sender Improvements
- **Automatic HTML and Markdown handling** – processes HTML tags and Markdown formatting applied via `Bold(...)`, `Sanitize(...)`, etc.  
- **Enhanced Sender logic** – automatically sanitizes content in style blocks and assigns the correct `parse_mode`.  
- New methods:
  - `sender.set_media(...)`
  - `chain.create_sender(chat_id)`

### Telekit Utilities
- `telekit.enable_file_logging()`  

### Telekit DSL
- Added types: `none`, `true`, `false` (case-insensitive)  
- Parser prevents creation of scenes with reserved name `back`  
- New syntax:
  - `row_width` syntax: `buttons[2]` → `buttons(2)`  
- `TelekitDSL.from_file(...)` and `TelekitDSL.from_string(...)`  
- Renamed `GuideMixin` → `TelekitDSL.Mixin`
  - Buttons without labels supported ([details](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#buttons-without-label))  
- Full Telekit DSL Documentation updated

### Chain Utilities
- `handler.new_chain() -> None` - creates a new chain
- `chain.remove_all_handlers()` – removes all callback handlers  
- `chain.remove_timeout()` – removes active timeout  
- `chain.remove_entry_handler()` – removes current entry handler  
- `chain.remove_inline_keyboard()` – removes inline keyboard and callback bindings  
- Automatic removal after `chain.send()` or `.edit()`, but can be disabled:
  - `chain.set_remove_timeout(False)`
  - `chain.set_remove_entry_handler(False)`
  - `chain.set_remove_inline_keyboard(False)`

### Tutorials
- New tutorial: [Tutorial](docs/tutorial/0_tutorial.md)  
- Other miscellaneous improvements

---

## ⚠️ Breaking Changes
- `GuideKit` and `GuideMixin` renamed → `TelekitDSL` and `TelekitDSL.Mixin`  
- `GuideKit(...)` replaced → `TelekitDSL.from_file(...)`  
- Removed methods:
  - `chain.set_always_edit_previous_message(...)`
  - `chain.parent` and all related functionality
  - `handler.get_child()`
  - `handler.get_chain(...)` → use `handler.new_chain()`
- Renamed for clarity:
  - `chain.edit_previous_message()` → `chain.mark_previous_message_for_edit()`
- Default `parse_mode` in DSL → `none`  
- DSL syntax updated: `buttons[2]` → `buttons(2)`

---

## ⏳ Delayed until v1.1.0
- DSL warning for strings with too many buttons or excessive text  
- Localization support for `self.user.enable_logging()` (currently global)

---

Old release notes are available in previous commits.