# Inline Button Types

Every value you pass to `set_inline_keyboard()` or `InlineKeyboard.add()` is an `InlineButton`.
Simple callables and strings are converted automatically — but for anything beyond that, you use one of the concrete button classes directly.

```python
InlineKeyboard()
    .add_callback("Hello!", self.callback)
    # equivalent to:
    .add("Hello!", CallbackButton(self.callback))
```

## Button Types

<details>
<summary><code>LinkButton</code> — opens a URL</summary>

```python
self.chain.set_inline_keyboard({
    "GitHub": LinkButton("https://github.com/Romashkaa/telekit"),
    "Telegram": LinkButton("tg://user?id=123456789"),
})
```

| **Param** | **Type** | **Description**               |
| --------- | -------- | ----------------------------- |
| `url`     | `str`    | HTTP or `tg://` URL to open.  |
| `style`   | `str \| ButtonStyle \| None` | Button colour. |

</details>

<details>
<summary><code>WebAppButton</code> — opens a Telegram Mini App</summary>

```python
self.chain.set_inline_keyboard({
    "Open App": WebAppButton("https://my-app.example.com"),
})
```

| **Param** | **Type** | **Description**                        |
| --------- | -------- | -------------------------------------- |
| `url`     | `str`    | HTTPS URL of the Web App to open.      |
| `style`   | `str \| ButtonStyle \| None` | Button colour. |

</details>

<details>
<summary><code>SuggestButton</code> — simulates the user sending a message</summary>

When pressed, the button invisibly sends the suggestion text as if the user typed and sent it themselves — triggering any matching text handler in your bot.

```python
self.chain.set_inline_keyboard({
    "Say Hello": SuggestButton("Hello!"),
})
```

So if you have a handler registered for `"Hello!"`, it will be triggered automatically.

| **Param**    | **Type** | **Description**                         |
| ------------ | -------- | --------------------------------------- |
| `suggestion` | `str`    | Text to suggest (1–64 bytes).           |
| `strict`     | `bool`   | Raise on oversized input. Default `True`. |
| `style`      | `str \| ButtonStyle \| None` | Button colour. |

</details>

<details>
<summary><code>CopyTextButton</code> — copies text to the clipboard</summary>

```python
self.chain.set_inline_keyboard({
    "Copy Token": CopyTextButton("my-secret-token"),
})
```

| **Param** | **Type** | **Description**                           |
| --------- | -------- | ----------------------------------------- |
| `text`    | `str`    | Text to copy (1–256 characters).          |
| `strict`  | `bool`   | Raise on oversized input. Default `True`. |
| `style`   | `str \| ButtonStyle \| None` | Button colour.  |

</details>

<details>
<summary><code>CallbackButton</code> — fires a callback with arguments</summary>

Use this when you need to pass arguments to the callback — something a plain `Callable` reference can't do.

```python
self.chain.set_inline_keyboard({
    "Delete": CallbackButton(
        self.handle_delete,
        pass_args=[item_id],
        style=ButtonStyle.DANGER,
    ),
    "Confirm": CallbackButton(
        self.handle_confirm,
        answer_text="Done!",
        answer_as_alert=False,
    ),
})
```

| **Param**         | **Type**            | **Description**                                          |
| ----------------- | ------------------- | -------------------------------------------------------- |
| `callback`        | `Callable`          | Function to call when pressed.                           |
| `pass_args`       | `list \| tuple \| None` | Positional arguments forwarded to the callback.      |
| `pass_kwargs`     | `dict \| None`      | Keyword arguments forwarded to the callback.             |
| `answer_text`     | `str \| None`       | Text shown to the user after the button is pressed.      |
| `answer_as_alert` | `bool`              | Show `answer_text` as a popup alert. Default `True`.     |
| `style`           | `str \| ButtonStyle \| None` | Button colour.                                |

</details>

<details>
<summary><code>StaticButton</code> — decorative, no action</summary>

A non-interactive button. Useful as a label or visual separator inside a keyboard.

```python
InlineKeyboard()
    .add_static("── Settings ──")
    .row()
    .add_callback("Theme", self.handle_theme)
    .add_callback("Language", self.handle_language)
```

| **Param** | **Type** | **Description** |
| --------- | -------- | --------------- |
| `style`   | `str \| ButtonStyle \| None` | Button colour. |

</details>

## Answer Buttons

These buttons respond to a press with a Telegram notification or alert — without invoking a callback. Useful for cancellation, info labels, or session-ending actions.

Both support a `persistent` parameter:
- `True` *(default)* — the button is a non-blocking hint; the session continues.
- `False` — terminates the session after the button is pressed.

<details>
<summary><code>AlertButton</code> — shows a popup dialog</summary>

```python
self.chain.set_inline_keyboard({
    "✕ Cancel": AlertButton("Action cancelled."),
})
```

| **Param**    | **Type**  | **Description**                              |
| ------------ | --------- | -------------------------------------------- |
| `text`       | `str \| None` | Text shown in the alert popup.           |
| `persistent` | `bool`    | If `False`, terminates the session. Default `True`. |
| `style`      | `str \| ButtonStyle \| None` | Button colour.          |

</details>

<details>
<summary><code>NotificationButton</code> — shows a brief top-of-chat notification</summary>

```python
self.chain.set_inline_keyboard({
    "✕ Cancel": NotificationButton("Cancelled."),
})
```

| **Param**    | **Type**  | **Description**                                     |
| ------------ | --------- | --------------------------------------------------- |
| `text`       | `str \| None` | Text shown in the notification.                 |
| `persistent` | `bool`    | If `False`, terminates the session. Default `True`. |
| `style`      | `str \| ButtonStyle \| None` | Button colour.                   |

</details>

## InvokeButton

Resolves and calls a named method on any object at press time. Unlike `CallbackButton`, the method is looked up via `getattr(obj, invoke)`.

<details>
<summary><code>InvokeButton</code> — calls a method on an arbitrary object</summary>

```python
self.chain.set_inline_keyboard({
    "📖 My Deck": InvokeButton(self.handoff(DeckHandler), "handle"),
})
```

| **Param**         | **Type**       | **Description**                                       |
| ----------------- | -------------- | ----------------------------------------------------- |
| `obj`             | `Any`          | Object on which the method will be called.            |
| `invoke`          | `str`          | Name of the method to call.                           |
| `pass_args`       | `list \| tuple \| None` | Positional arguments forwarded to the method. |
| `pass_kwargs`     | `dict \| None` | Keyword arguments forwarded to the method.            |
| `answer_text`     | `str \| None`  | Text shown after the button is pressed.               |
| `answer_as_alert` | `bool`         | Show `answer_text` as a popup. Default `True`.        |
| `style`           | `str \| ButtonStyle \| None` | Button colour.                         |

</details>

## Button Styles

All button types accept a `style` parameter to change the button colour:

| **Value**              | **Colour** |
| ---------------------- | ---------- |
| `ButtonStyle.DANGER`   | Red        |
| `ButtonStyle.SUCCESS`  | Green      |
| `ButtonStyle.PRIMARY`  | Blue       |

Styles can be passed as enum values or plain strings:

```python
CallbackButton(self.delete, style=ButtonStyle.DANGER)
CallbackButton(self.delete, style="danger")  # equivalent
```

---

> In the next section we'll cover user input with entries.

[Next: Entries »](8_entries.md)