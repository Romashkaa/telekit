## Chain Improvements

- `set_entry` - general callback for any message.
- `set_entry_text` - callback for text messages only.
- `set_entry_photo` - callback for photo messages.
- `set_entry_document` - callback for document messages.
- `set_entry_text_document` - callback for text-based documents; auto-downloads and decodes text.
- `set_entry_location` - callback for location messages.

## DSL Improvements

- You can now use `text=` directly instead of separate `title` and `message` fields.
- Complete refactor of the rendering process, resulting in improved performance.