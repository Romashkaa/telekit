## Chain Improvements

- New methods:
    - `set_entry` - general callback for any message.
    - `set_entry_text` - callback for text messages only.
    - `set_entry_photo` - callback for photo messages.
    - `set_entry_document` - callback for document messages.
    - `set_entry_text_document` - callback for text-based documents; auto-downloads and decodes text.
    - `set_entry_location` - callback for location messages.
    - Each of these methods has a corresponding decorator with the same name, but without the `set_` prefix.
        - Setter:
        ```python
        def handle_name(self, message: Message, name: str):
            print(name)

        def handle(self):
            ...
            self.chain.set_entry_text(self.handle_name) # self.handle_name: Callable[[Message, name], Any]
            self.chain.send()
        ```
        - Decorator:
        ```py
        def handle(self):
            ...
            @self.chain.entry_text()
            def _handle_name(message: Message, name: str):
                print(name)
                
            self.chain.send()
        ```

## DSL Improvements

- You can now use `text=` directly instead of separate `title` and `message` fields.
- Complete refactor of the rendering process.
- Improved performance.