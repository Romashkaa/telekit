# Reply Button Types

Every button added to a `ReplyKeyboard` is a `ReplyButton`. The typed helpers on `ReplyKeyboard` cover the common cases — but you can also pass button instances directly to `add()` or `extend()` when you need more control.

```python
from telekit.reply_buttons import (
    TextButton, ContactButton, LocationButton,
    PollButton, WebAppReplyButton,
    RequestUserButton, RequestChatButton,
)
```

## Button Types

<details>
<summary><code>TextButton</code> — sends the label as a message</summary>

The default button type. When pressed, the button label is sent as a regular user message — triggering any matching text handler in your bot.

```python
ReplyKeyboard()
    .add_text("Hello!")
    # equivalent to:
    .add("Hello!", TextButton())
```

</details>

<details>
<summary><code>ContactButton</code> — requests the user's phone number</summary>

Telegram prompts the user to share their contact. The bot receives a `contact` message with the phone number and name.

Only works in private chats.

```python
ReplyKeyboard()
    .add_contact("📱 Share phone number")
    # equivalent to:
    .add("📱 Share phone number", ContactButton())
```

</details>

<details>
<summary><code>LocationButton</code> — requests the user's geolocation</summary>

Telegram prompts the user to share their current location. The bot receives a `location` message with latitude and longitude.

Only works in private chats.

```python
ReplyKeyboard()
    .add_location("📍 Share location")
    # equivalent to:
    .add("📍 Share location", LocationButton())
```

</details>

<details>
<summary><code>PollButton</code> — prompts the user to create a poll</summary>

Opens Telegram's poll creation interface. You can optionally restrict the poll type.

```python
ReplyKeyboard()
    .add_poll("📊 Create poll")                    # any type
    .add_poll("🧠 Create quiz", poll_type="quiz")  # quiz only
    .add_poll("📋 Create survey", poll_type="regular")
    # equivalent to:
    .add("📊 Create poll", PollButton())
    .add("🧠 Create quiz", PollButton(poll_type="quiz"))
```

| **Param**   | **Type**      | **Description**                                                  |
| ----------- | ------------- | ---------------------------------------------------------------- |
| `poll_type` | `str \| None` | `"quiz"`, `"regular"`, or `None` for any type. Default `None`.  |

</details>

<details>
<summary><code>WebAppReplyButton</code> — opens a Telegram Mini App</summary>

Opens the specified Web App when pressed.

```python
ReplyKeyboard()
    .add_webapp("🌐 Open App", "https://my-app.example.com")
    # equivalent to:
    .add("🌐 Open App", WebAppReplyButton(url="https://my-app.example.com"))
```

| **Param** | **Type** | **Description**               |
| --------- | -------- | ----------------------------- |
| `url`     | `str`    | HTTPS URL of the Web App.     |

</details>

<details>
<summary><code>RequestUserButton</code> — prompts the user to select another Telegram user</summary>

Telegram opens a user picker. The selected user's ID is sent back as a service message.

```python
ReplyKeyboard()
    .add_request_user("👤 Select a user", request_id=1)
    .add_request_user("🤖 Select a bot", request_id=2, user_is_bot=True)
    .add_request_user("⭐ Select Premium user", request_id=3, user_is_premium=True)
    # equivalent to:
    .add("👤 Select a user", RequestUserButton(request_id=1))
```

| **Param**         | **Type**       | **Description**                                                 |
| ----------------- | -------------- | --------------------------------------------------------------- |
| `request_id`      | `int`          | Unique signed 32-bit identifier for this request.               |
| `user_is_bot`     | `bool \| None` | `True` — bots only, `False` — humans only, `None` — no filter. |
| `user_is_premium` | `bool \| None` | `True` — Premium only, `False` — non-Premium only, `None` — no filter. |

</details>

<details>
<summary><code>RequestChatButton</code> — prompts the user to select a chat</summary>

Telegram opens a chat picker. The selected chat's ID is sent back as a service message.

```python
ReplyKeyboard()
    .add_request_chat("💬 Select a group", request_id=1)
    .add_request_chat("📢 Select a channel", request_id=2, chat_is_channel=True)
    # equivalent to:
    .add("💬 Select a group", RequestChatButton(request_id=1))
```

| **Param**                   | **Type**                          | **Description**                                       |
| --------------------------- | --------------------------------- | ----------------------------------------------------- |
| `request_id`                | `int`                             | Unique signed 32-bit identifier for this request.     |
| `chat_is_channel`           | `bool`                            | `True` — channels only, `False` — groups only.        |
| `chat_is_forum`             | `bool \| None`                    | Only forum supergroups.                               |
| `chat_has_username`         | `bool \| None`                    | Only public chats.                                    |
| `chat_is_created`           | `bool \| None`                    | Only chats created by the user.                       |
| `user_administrator_rights` | `ChatAdministratorRights \| None` | Required user admin rights in the selected chat.      |
| `bot_administrator_rights`  | `ChatAdministratorRights \| None` | Required bot admin rights in the selected chat.       |
| `bot_is_member`             | `bool \| None`                    | Bot must already be a member of the selected chat.    |

</details>

---

[Next: Entries »](8_entries.md)