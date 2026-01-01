## DSL Improvements

- Added support for calling python `Handler` methods via `on_enter` and `on_enter_once` hooks:
    ```js
    @ throne_room {
        title = "🏰 Castle Ending 1"
        message = "You claim the throne. Victory!"
        
        on_enter {
            add_ending("throne_room")
        }
    }
    ```
    Each time this scene is displayed (either via a direct link, or using `back` or `next`), the `add_ending` method of the `Handler` object will be called with the parameter `"throne_room"`. [See documentation](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#calling-python-methods-in-dsl)

- Fixed formatting of the "No timeout configured" warning:
    ```js
    YYYY-MM-DD HH:MM:SS | WARNING | mixin.py | No timeout configured for this DSL script. It is recommended to add a timeout to automatically clear callbacks after a period of inactivity.

    Example:

    $ timeout {
        time = 30; // seconds
    }

    @ main {
        title = "🏰 Adventure Quest"
        message = "Welcome, {{first_name}}! Can you disc...

    Learn more about DSL Timeouts in the GitHub tutorial: https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#timeout
    ```