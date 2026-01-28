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
- New button type: "return" – navigates to the specified scene and clears the history between the current state and the target scene.  
  For example, if the history looks like [`a`, `b`, `previous`, `rooms`, `d`, `f`, `current`] and `return("Menu ↺", "rooms")` is called from the `current` scene, the history after the transition becomes [`a`, `b`, `previous`, `rooms`]. (not [`a`, `b`, `previous`, `rooms`, `d`, `f`, `current`, `rooms`] as would happen with a regular `rooms("Menu ↺")`)
  This allows the `back` button in the `rooms` scene to return the user not to the `current` scene, but to the `previous`.  
  If the target scene (`rooms`) appears multiple times in the history, `return` moves to the **last occurrence** of the target scene.
- Complete refactor of the rendering process.
- Improved performance.