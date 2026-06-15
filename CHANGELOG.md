## Inline and Reply Keyboards

### `chain.set_keyboard()`

Universal method for attaching a keyboard to the current chain message.
Accepts either an `InlineKeyboard` or a `ReplyKeyboard` instance.

```python
# Inline keyboard
self.chain.set_keyboard(
    InlineKeyboard()
        .add_callback("Click Me!", self.handle)
    .row()
        .add_link("YouTube", "https://youtube.com")
)

# Reply keyboard
self.chain.set_keyboard(
    ReplyKeyboard(one_time_keyboard=True)
        .add_text("Hello!")
        .add_text("Hi")
    .row()
        .add_contact("📱 Share phone")
)
```

> [!NOTE]
> Inline and reply keyboards are mutually exclusive in Telegram.
> Only one keyboard can be displayed at a time per message.
> Passing an `InlineKeyboard` attaches buttons directly to the message;
> passing a `ReplyKeyboard` replaces the user's system keyboard below the input field.

### `InlineKeyboard`

Fluent builder for Telegram inline keyboards. Supports all standard inline button types, conditional rendering via `when=`, and row/column layout helpers.

**Layout helpers**

| **Method**     | **Description** |
| -------------- | --------------- |
| `row()`        | Finalize the current row and start a new one. |
| `column()`     | Every subsequent button gets its own row. Alias for `grid(1)`. |
| `column_end()` | Exit column mode and flush the current row. Alias for `grid_end()`. |
| `grid(width)`  | Every subsequent button is automatically split into rows of `width` buttons. |
| `grid_end()`   | Exit grid mode and flush the current row. |

**Button methods**

| **Method** | **Description** |
|------------|-----------------|
| `add(text, button, when=)` | Attach any `InlineButton` instance. |
| `add_callback(text, callback, pass_args, pass_kwargs, answer_text, answer_as_alert, style, when=)` | Button that fires a callback function. |
| `add_link(text, url, style, when=)` | Button that opens a URL or `tg://` link. |
| `add_webapp(text, url, style, when=)` | Button that opens a Telegram Mini App. |
| `add_suggest(text, suggestion, style, strict, when=)` | Button that simulates the user sending a message. |
| `add_copy(text, copy_text, style, strict, when=)` | Button that copies text to the clipboard. |
| `add_static(text, style, when=)` | Decorative button with no action. |
| `add_alert(text, alert_text, persistent, style, when=)` | Button that shows a popup alert dialog. |
| `add_notification(text, notification_text, persistent, style, when=)` | Button that shows a brief top-of-chat notification. |
| `add_invoke(text, obj, invoke, pass_args, pass_kwargs, answer_text, answer_as_alert, style, when=)` | Button that calls a named method on an arbitrary object. |

**Bulk helpers**

| **Method** | **Description** |
|------------|-----------------|
| `extend(buttons, column=, when=)` | Add multiple buttons from a `dict[str, InlineButton \| None]` or `list[str]`. |
| `extend_rows(*rows, when=)` | Append one or more pre-built `list[tuple[str, InlineButton]]` rows. |

All button methods accept a `style` parameter: `"danger"` (red), `"success"` (green), or `"primary"` (blue).

```python
InlineKeyboard()
    .add_link("YouTube", "https://youtube.com")
    .add_copy("Copy Me", "copied!")
    .add_alert("Info", "This is an alert")
.row()
    .add_callback("Click Me!", self.handle)
.column()
    .add_link("A", "https://example.com")
    .add_callback("B", self.handle_b)
.column_end()
.extend({"Alert": AlertButton("Hi!"), "Notify": NotificationButton("Hey")}, column=True)
```

### `ReplyKeyboard`

Fluent builder for Telegram reply keyboards. Mirrors the `InlineKeyboard` layout API (`row`, `column`, `column_end`, `extend`, `extend_rows`).

**Constructor parameters**

| **Parameter** | **Default** | **Description** |
|---|---|---|
| `resize_keyboard` | `True` | Shrink the keyboard to fit its buttons. |
| `one_time_keyboard` | `False` | Hide the keyboard after the first press. |
| `input_field_placeholder` | `None` | Placeholder text shown while the keyboard is active (max 64 chars). |
| `selective` | `False` | Show only to mentioned users or the original sender. |
| `is_persistent` | `False` | Always show the keyboard; do not collapse it to an icon. |

**Button methods**

| **Method** | **Description** |
|---|---|
| `add(text, button, when=)` | Attach any `ReplyButton` instance. |
| `add_text(text, when=)` | Plain text button — sends the label as a message. |
| `add_contact(text, when=)` | Prompts the user to share their phone number (private chats only). |
| `add_location(text, when=)` | Prompts the user to share their geolocation (private chats only). |
| `add_poll(text, poll_type, when=)` | Opens the poll creation dialog; `poll_type` can be `"quiz"`, `"regular"`, or `None`. |
| `add_webapp(text, url, when=)` | Opens a Telegram Mini App. |
| `add_request_user(text, request_id, user_is_bot, user_is_premium, when=)` | Lets the user pick a Telegram user; result returned as a service message. |
| `add_request_chat(text, request_id, chat_is_channel, chat_is_forum, chat_has_username, chat_is_created, user_administrator_rights, bot_administrator_rights, bot_is_member, when=)` | Lets the user pick a chat; result returned as a service message. |

```python
ReplyKeyboard(input_field_placeholder="Choose:", one_time_keyboard=True)
    .add_text("Hello!")
    .add_text("Hi")
.row()
    .add_contact("📱 Phone")
    .add_location("📍 Location")
    .add_poll("📊 Poll")
.row()
    .add_request_user("Pick user", request_id=1)
    .add_request_chat("Pick chat", request_id=2)
```

## Telekit DSL

### `InstanceDSLHandler`

Instance-oriented variant of `DSLHandler` where each instance carries its own
`executable_model`, `_script_data_factory`, and `_jinja_env` — allowing multiple
instances to run completely independent scripts simultaneously.

Use the `*_locally` instance methods instead of the class-level ones:

```python
class MyHandler(telekit.InstanceDSLHandler):
    @classmethod
    def init_handler(cls) -> None:
        cls.on.message().invoke(cls.handle)

    def handle(self):
        script = fetch_script_from_db(self.user.id)  # per-user DSL
        self.analyze_string_locally(script)
        self.start_script()
```

| **Method**                              | **Description**                                      |
| --------------------------------------- | ---------------------------------------------------- |
| `analyze_file_locally(path, encoding)`  | Analyse a script file on this instance.              |
| `analyze_string_locally(script)`        | Analyse a DSL string on this instance.               |
| `analyze_canvas_locally(file_path)`     | Analyse an Obsidian `.canvas` file on this instance. |
| `analyze_executable_model_locally(model)` | Load a pre-built model dict on this instance.      |

**Security**

When accepting scripts from untrusted users, restrict dangerous features via the
`RESTRICTED` class attribute. Set `DEFAULT_TIMEOUT` to control the fallback timeout,
and `DEFAULT_CONFIG` to provide a safe base config.

```python
class SafeDSL(telekit.InstanceDSLHandler):
    RESTRICTED: list[RestrictedToken] = ["hook", "jinja", "redirect", "handoff", "config"]
    DEFAULT_TIMEOUT = 120
    DEFAULT_CONFIG  = {"template": "vars"}
```

| **Token**      | **Effect**                                                                                      |
| -------------- | ----------------------------------------------------------------------------------------------- |
| `"handoff"`    | Disables `handoff` button type (cross-handler transitions).                                     |
| `"redirect"`   | Disables `redirect` button type (simulated user messages).                                      |
| `"hook"`       | Removes all `on_enter`, `on_enter_once`, `on_exit`, `on_timeout` hooks.                        |
| `"jinja"`      | Forces template engine to `"vars"`; Jinja is never executed.                                    |
| `"timeout"`    | Ignores per-script `timeout_time`; uses `DEFAULT_TIMEOUT` only.                                 |
| `"config"`     | Replaces script config with `DEFAULT_CONFIG`; `vars_*` keys are preserved unless `"vars"` is also set. |
| `"vars"`       | Removes all `vars_*` keys and disables `{{variable}}` substitution.                             |
| `"images"`     | Strips `image` field from every scene.                                                          |
| `"links"`      | Disables `link` button type (external URLs).                                                    |
| `"suggest"`    | Disables `suggest` button type (pre-filled entry suggestions).                                  |
| `"entry"`      | Disables entry handlers (free-text input routing).                                              |
| `"next"`       | Disables `next` magic scene navigation.                                                         |
| `"back"`       | Disables `back` magic scene navigation.                                                         |

## Scheduler

- Added `every` decorator for scheduling functions in a background daemon thread.
- Implemented `PeriodicTask` class to manage periodic execution and error handling.

## Others

- Enhanced `Debug` class with callback query tracing functionality.
- Refactored `BaseSender` to use `send_or_handle_error`.