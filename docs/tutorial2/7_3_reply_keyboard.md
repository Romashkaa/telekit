# Reply Keyboard

A reply keyboard replaces the user's system keyboard with a row of buttons at the bottom of the screen. When the user taps one, it sends the button's text as a regular message — or triggers a system action like sharing a phone number or location.

Unlike inline keyboards, reply keyboards are not attached to a specific message. They persist until explicitly removed or replaced.

```python
from telekit.types import ReplyKeyboard

self.chain.set_keyboard(
    ReplyKeyboard(one_time_keyboard=True)
        .add_text("Option A")
        .add_text("Option B")
    .row()
        .add_contact("📱 Share phone number")
)
self.chain.send()
```

> [!NOTE]
> Inline and reply keyboards are mutually exclusive — only one can be active per message.

## Constructor Parameters

| **Param** | **Type** | **Default** | **Description** |
| --------- | -------- | ----------- | --------------- |
| `resize_keyboard` | `bool` | `True` | Shrink the keyboard to fit its buttons. |
| `one_time_keyboard` | `bool` | `False` | Hide the keyboard after the first button press. |
| `input_field_placeholder` | `str \| None` | `None` | Placeholder text shown in the input field while the keyboard is active. |
| `selective` | `bool` | `False` | Show the keyboard only to mentioned users or the message sender. |
| `is_persistent` | `bool` | `False` | Always show the keyboard; do not collapse it to a small icon. |

## Layout

Layout works identically to `InlineKeyboard` — use `.row()` to start a new row, `.column_start()` / `.column_end()` for a vertical stack:

```python
ReplyKeyboard()
    .add_text("A")
    .add_text("B")
    .add_text("C")
.row()
    .add_contact("📱 Share phone")
```

```
╭──────┬──────┬──────╮
│  A   │  B   │  C   │
├──────┴──────┴──────┤
│   📱 Share phone   │
╰────────────────────╯
```

## Button Methods

| **Method**               | **Description**                                                        |
| ------------------------ | ---------------------------------------------------------------------- |
| `add_text(text)`         | Sends the label as a regular message when pressed.                     |
| `add_contact(text)`      | Prompts the user to share their phone number. Private chats only.      |
| `add_location(text)`     | Prompts the user to share their geolocation. Private chats only.       |
| `add_poll(text, poll_type)` | Prompts the user to create a poll. `poll_type`: `"quiz"`, `"regular"`, or `None` for any. |
| `add_webapp(text, url)`  | Opens a Telegram Mini App at the given HTTPS URL.                      |
| `add_request_user(text, request_id, ...)` | Prompts the user to select another Telegram user.     |
| `add_request_chat(text, request_id, ...)` | Prompts the user to select a chat.                    |
| `add(text, button)`      | Attach any `ReplyButton` instance directly.                            |
| `extend(buttons)`        | Add multiple buttons from a `dict` or `list[str]`.                     |
| `extend_rows(*rows)`     | Append pre-built rows of `(label, ReplyButton)` tuples.                |

All methods accept `when=` for conditional rendering:

```python
ReplyKeyboard()
    .add_contact("📱 Share phone", when=not self.user_has_phone)
    .add_text("Skip")
```

## `add_request_user` Parameters

| **Param**          | **Type**       | **Description**                                                  |
| ------------------ | -------------- | ---------------------------------------------------------------- |
| `request_id`       | `int`          | Unique signed 32-bit identifier for this request.                |
| `user_is_bot`      | `bool \| None` | `True` — bots only, `False` — humans only, `None` — no filter.  |
| `user_is_premium`  | `bool \| None` | `True` — Premium only, `False` — non-Premium only, `None` — no filter. |

## `add_request_chat` Parameters

| **Param**                   | **Type**       | **Description**                                             |
| --------------------------- | -------------- | ----------------------------------------------------------- |
| `request_id`                | `int`          | Unique signed 32-bit identifier for this request.           |
| `chat_is_channel`           | `bool`         | `True` — channels only, `False` — groups only.              |
| `chat_is_forum`             | `bool \| None` | Only forum supergroups.                                     |
| `chat_has_username`         | `bool \| None` | Only public chats.                                          |
| `chat_is_created`           | `bool \| None` | Only chats created by the user.                             |
| `user_administrator_rights` | `ChatAdministratorRights \| None` | Required user admin rights in the chat.  |
| `bot_administrator_rights`  | `ChatAdministratorRights \| None` | Required bot admin rights in the chat.   |
| `bot_is_member`             | `bool \| None` | Bot must already be a member of the chat.                   |

---

> In the next file we'll cover all reply button types individually.

[Next: Reply Button Types »](./7_4_reply_buttons.md)