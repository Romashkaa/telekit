## DSL Improvements

- Added `initial_scene` parameter for `start_script` method
- Added new button types:
    - `redirect(label, text)` — creates a button that simulates the user sending a specific message or command. Clicking it automatically ends the current script.
    - `handoff(label, handler_name)` — creates a button that seamlessly switches control to another handler. Equivalent to calling `self.handoff(handler_name).handle()` in code.
    - See tutorial:
        - [Handoff Button](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#handoff-button)
        - [Redirect Button](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#redirect-button)