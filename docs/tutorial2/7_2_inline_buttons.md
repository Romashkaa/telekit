# Inline Button Types

Inline keyboards are built with `InlineKeyboard` and attached to a message with `set_keyboard()`.
Every button is added with an `add_*` method, one per button type:

```python
self.chain.set_keyboard(
    InlineKeyboard()
        .add_callback("Hello!", self.callback)
        .add_link("GitHub", "https://github.com/Romashkaa/telekit")
    .row()
        .add_copy("Copy", "hello")
)
```

Under the hood, every `add_*` method creates an `InlineButton` object. When you need more control, you can create that object yourself and pass it to `.add()` or `.extend()`:

```python
InlineKeyboard()
    .add_callback("Hello!", self.callback)
    # equivalent to:
    .add("Hello!", CallbackButton(self.callback))
```

> [!NOTE]
> Callback-based buttons (`add_callback`, `add_invoke`, `add_alert`, `add_notification`) need a chain to register their handlers, so they only work with `chain.set_keyboard()`. A standalone sender supports only link, web app, suggest, copy and static buttons.

## Button Types

<details>
<summary><code>add_callback</code> — fires a callback, optionally with arguments</summary>

```python
InlineKeyboard()
    .add_callback("Delete", self.handle_delete, pass_args=[item_id], style="danger")
    .add_callback("Confirm", self.handle_confirm, answer_text="Done!", answer_as_alert=False)
```

| **Param**         | **Type**                     | **Description**                                      |
| ----------------- | ---------------------------- | ---------------------------------------------------- |
| `text`            | `str`                        | Button label.                                        |
| `callback`        | `Callable`                   | Function to call when pressed.                       |
| `pass_args`       | `list \| tuple \| None`      | Positional arguments forwarded to the callback.      |
| `pass_kwargs`     | `dict \| None`               | Keyword arguments forwarded to the callback.         |
| `answer_text`     | `str \| None`                | Text shown to the user after the button is pressed.  |
| `answer_as_alert` | `bool`                       | Show `answer_text` as a popup alert. Default `True`. |
| `style`           | `str \| ButtonStyle \| None` | Button colour.                                       |
| `when`            | `bool`                       | If `False`, the button is not added.                 |

**Class form:** `CallbackButton(callback, pass_args, pass_kwargs, answer_text=..., answer_as_alert=..., style=...)`

```python
InlineKeyboard()
    .add("Delete", CallbackButton(self.handle_delete, pass_args=[item_id], style=ButtonStyle.DANGER))
```

</details>

<details>
<summary><code>add_link</code> — opens a URL</summary>

```python
InlineKeyboard()
    .add_link("GitHub", "https://github.com/Romashkaa/telekit")
    .add_link("Telegram", "tg://user?id=123456789")
```

| **Param** | **Type**                     | **Description**              |
| --------- | ---------------------------- | ---------------------------- |
| `text`    | `str`                        | Button label.                |
| `url`     | `str`                        | HTTP or `tg://` URL to open. |
| `style`   | `str \| ButtonStyle \| None` | Button colour.               |
| `when`    | `bool`                       | If `False`, the button is not added. |

**Class form:** `LinkButton(url, style=...)`

```python
InlineKeyboard()
    .add("GitHub", LinkButton("https://github.com/Romashkaa/telekit"))
```

</details>

<details>
<summary><code>add_contact</code>, <code>add_user_link</code>, <code>add_bot_link</code> — Telegram link shortcuts</summary>

Shortcuts that build `tg://` and `t.me` links for you:

```python
InlineKeyboard()
    .add_contact("👤 Profile", 123456789)                      # tg://user?id=...
    .add_user_link("💬 Write to me", "Username", "Hi!")      # t.me/<username>, optional pre-filled message
.row()
    .add_bot_link("🚀 Open bot", "MyBot", start="promo_42")    # t.me/<bot>?start=...
```

| **Method**       | **Params**                           | **Class form**                          |
| ---------------- | ------------------------------------ | --------------------------------------- |
| `add_contact`    | `text`, `user_id`                    | `ContactButton(user_id)`                |
| `add_user_link`  | `text`, `username`, `message=None`   | `UserLinkButton(username, message)`     |
| `add_bot_link`   | `text`, `botname`, `start=None`      | `BotLinkButton(botname, start)`         |

All of them also accept `style` and `when`.

</details>

<details>
<summary><code>add_webapp</code> — opens a Telegram Mini App</summary>

```python
InlineKeyboard()
    .add_webapp("Open App", "https://my-app.example.com")
```

| **Param** | **Type**                     | **Description**                   |
| --------- | ---------------------------- | --------------------------------- |
| `text`    | `str`                        | Button label.                     |
| `url`     | `str`                        | HTTPS URL of the Web App to open. |
| `style`   | `str \| ButtonStyle \| None` | Button colour.                    |
| `when`    | `bool`                       | If `False`, the button is not added. |

**Class form:** `WebAppButton(url, style=...)`

```python
InlineKeyboard()
    .add("Open App", WebAppButton("https://my-app.example.com"))
```

</details>

<details>
<summary><code>add_suggest</code> — simulates the user sending a message</summary>

When pressed, the button invisibly sends the suggestion text as if the user typed and sent it themselves, triggering any matching text handler in your bot.

```python
InlineKeyboard()
    .add_suggest("Say Hello", "Hello!")
```

So if you have a handler registered for `"Hello!"`, it will be triggered automatically.

| **Param**    | **Type**                     | **Description**                           |
| ------------ | ---------------------------- | ----------------------------------------- |
| `text`       | `str`                        | Button label.                             |
| `suggestion` | `str`                        | Text to suggest (1–64 bytes).             |
| `strict`     | `bool`                       | Raise on oversized input. Default `True`. |
| `style`      | `str \| ButtonStyle \| None` | Button colour.                            |
| `when`       | `bool`                       | If `False`, the button is not added.      |

**Class form:** `SuggestButton(suggestion, strict=..., style=...)`

```python
InlineKeyboard()
    .add("Say Hello", SuggestButton("/start"))
```

</details>

<details>
<summary><code>add_copy</code> — copies text to the clipboard</summary>

```python
InlineKeyboard()
    .add_copy("Copy Token", "my-secret-token")
```

| **Param**   | **Type**                     | **Description**                           |
| ----------- | ---------------------------- | ----------------------------------------- |
| `text`      | `str`                        | Button label.                             |
| `copy_text` | `str`                        | Text to copy (1–256 characters).          |
| `strict`    | `bool`                       | Raise on oversized input. Default `True`. |
| `style`     | `str \| ButtonStyle \| None` | Button colour.                            |
| `when`      | `bool`                       | If `False`, the button is not added.      |

**Class form:** `CopyTextButton(text, strict=..., style=...)`

```python
InlineKeyboard()
    .add("Copy Token", CopyTextButton("my-secret-token"))
```

</details>

<details>
<summary><code>add_static</code> — decorative, no action</summary>

A non-interactive button. Useful as a label or visual separator inside a keyboard.

```python
InlineKeyboard()
    .add_static("── Settings ──")
.row()
    .add_callback("Theme", self.handle_theme)
    .add_callback("Language", self.handle_language)
```

| **Param** | **Type**                     | **Description**                      |
| --------- | ---------------------------- | ------------------------------------ |
| `text`    | `str`                        | Button label.                        |
| `style`   | `str \| ButtonStyle \| None` | Button colour.                       |
| `when`    | `bool`                       | If `False`, the button is not added. |

**Class form:** `StaticButton(style=...)`. This is also what `.add("text")` creates when you omit the button:

```python
InlineKeyboard()
    .add("── Settings ──")
```

</details>

## Answer Buttons

These buttons respond to a press with a Telegram notification or alert, without invoking a callback. Useful for cancellation, info labels, or session-ending actions.

Both support a `persistent` parameter:
- `True` *(default)*: the button is a non-blocking hint; the session continues.
- `False`: terminates the session after the button is pressed.

<details>
<summary><code>add_alert</code> — shows a popup dialog</summary>

```python
InlineKeyboard()
    .add_alert("✕ Cancel", "Action cancelled.")
```

| **Param**    | **Type**                     | **Description**                                     |
| ------------ | ---------------------------- | --------------------------------------------------- |
| `text`       | `str`                        | Button label.                                       |
| `alert_text` | `str \| None`                | Text shown in the alert popup.                      |
| `persistent` | `bool`                       | If `False`, terminates the session. Default `True`. |
| `style`      | `str \| ButtonStyle \| None` | Button colour.                                      |
| `when`       | `bool`                       | If `False`, the button is not added.                |

**Class form:** `AlertButton(text, persistent=..., style=...)`

```python
InlineKeyboard()
    .add("✕ Cancel", AlertButton("Action cancelled."))
```

</details>

<details>
<summary><code>add_notification</code> — shows a brief top-of-chat notification</summary>

```python
InlineKeyboard()
    .add_notification("✕ Cancel", "Cancelled.")
```

| **Param**           | **Type**                     | **Description**                                     |
| ------------------- | ---------------------------- | --------------------------------------------------- |
| `text`              | `str`                        | Button label.                                       |
| `notification_text` | `str \| None`                | Text shown in the notification.                     |
| `persistent`        | `bool`                       | If `False`, terminates the session. Default `True`. |
| `style`             | `str \| ButtonStyle \| None` | Button colour.                                      |
| `when`              | `bool`                       | If `False`, the button is not added.                |

**Class form:** `NotificationButton(text, persistent=..., style=...)`

```python
InlineKeyboard()
    .add("✕ Cancel", NotificationButton("Cancelled."))
```

</details>

## Invoke Button

Resolves and calls a named method on any object at press time. Unlike `add_callback`, the method is looked up via `getattr(obj, invoke)`.

<details>
<summary><code>add_invoke</code> — calls a method on an arbitrary object</summary>

```python
InlineKeyboard()
    .add_invoke("📖 My Deck", self.handoff(DeckHandler), "handle")
```

| **Param**         | **Type**                     | **Description**                                |
| ----------------- | ---------------------------- | ---------------------------------------------- |
| `text`            | `str`                        | Button label.                                  |
| `obj`             | `Any`                        | Object on which the method will be called.     |
| `invoke`          | `str`                        | Name of the method to call.                    |
| `pass_args`       | `list \| tuple \| None`      | Positional arguments forwarded to the method.  |
| `pass_kwargs`     | `dict \| None`               | Keyword arguments forwarded to the method.     |
| `answer_text`     | `str \| None`                | Text shown after the button is pressed.        |
| `answer_as_alert` | `bool`                       | Show `answer_text` as a popup. Default `True`. |
| `style`           | `str \| ButtonStyle \| None` | Button colour.                                 |
| `when`            | `bool`                       | If `False`, the button is not added.           |

**Class form:** `InvokeButton(obj, invoke, pass_args, pass_kwargs, ...)`

```python
InlineKeyboard()
    .add("📖 My Deck", InvokeButton(self.handoff(DeckHandler), "handle"))
```

</details>

## Using Button Classes Directly

The `*Button` classes are useful when you build buttons separately from the keyboard: in a loop, a helper function, or a pre-made dict. Pass them to `.add()` one at a time, or to `.extend()` all at once:

```python
buttons = {
    "GitHub": LinkButton("https://github.com/Romashkaa/telekit"),
    "Open App": WebAppButton("https://my-app.example.com"),
    "Copy": CopyTextButton("hello"),
}

self.chain.set_keyboard(
    InlineKeyboard()
        .extend(buttons, width=2)       # rows of 2 buttons
        .add_callback("« Back", self.handle)
)
```

`extend()` accepts a `dict` of `label → button`, or a plain `list` of labels (each becomes a `StaticButton`). `width` controls the row split: `False` puts everything in one row, `True` puts each button on its own row, and any `n >= 2` makes rows of `n` buttons.

You can also seed the keyboard at initialization with ready-made rows of `(text, button)` tuples:

```python
InlineKeyboard([
    [("GitHub", LinkButton("https://github.com/Romashkaa/telekit")),
     ("Copy",   CopyTextButton("hello"))],
    [("« Back", CallbackButton(self.handle))],
])
```

Or append fully-defined rows with `extend_rows()`:

```python
InlineKeyboard()
    .extend_rows(
        [("Option A", CallbackButton(self.on_a)), ("Option B", CallbackButton(self.on_b))],
        [("« Back",   CallbackButton(self.handle))],
    )
```

## Button Styles

All button types accept a `style` parameter to change the button colour:

| **Value**              | **Colour** |
| ---------------------- | ---------- |
| `ButtonStyle.DANGER`   | Red        |
| `ButtonStyle.SUCCESS`  | Green      |
| `ButtonStyle.PRIMARY`  | Blue       |

Styles can be passed as enum values or plain strings:

```python
InlineKeyboard()
    .add_callback("Delete", self.delete, style=ButtonStyle.DANGER)
    .add_callback("Delete", self.delete, style="danger")  # equivalent
```

---

> In the next section we'll cover user input with entries.

[Next: Entries »](8_entries.md)