# Handoff

Handoff transfers control from one handler to another while preserving chain continuity — the target handler receives the same user message and can edit the same bot message.

This is the primary way to navigate between handlers in Telekit.

```python
self.handoff(ProfileHandler).handle()
```

## How It Works

When you call `handoff()`, Telekit creates a new instance of the target handler and passes it:
- the **same user message** that triggered the current handler
- the **previous bot message**, so the new handler can edit it seamlessly

No state is lost, no new message is sent — the conversation continues as if the target handler had been invoked directly.

## Basic Usage

```python
class SettingsHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        cls.on.command("settings").invoke(cls.handle)

    def handle(self) -> None:
        self.chain.sender.set_title("⚙️ Settings")
        self.chain.sender.set_message("Choose a section:")
        self.chain.set_inline_keyboard({
            "👤 Profile":  self.handoff(ProfileHandler).handle,
            "🔔 Notifications": self.handoff(NotificationsHandler).handle,
        })
        self.chain.edit()
```

The target handler can be passed as a **class** or a **string name**:

```python
self.handoff(ProfileHandler).handle()   # by class
self.handoff("ProfileHandler").handle() # by name — resolved from the handler registry
```

## Handoff as a Button Callback

Since `handoff()` returns a handler instance, you can pass `.handle` directly as a button callback:

```python
self.chain.set_inline_keyboard({
    "« Back": self.handoff(StartHandler).handle,
})
```

When the user presses the button, `StartHandler.handle()` is called with the preserved chain context.

## Handoff from a Choice Keyboard

`handoff()` works naturally inside choice keyboards — the selected value is passed as the handler name or used to branch logic:

```python
@self.chain.inline_keyboard(
    {
        "🧮 Counter": "CounterHandler",
        "📖 Pages":   "PagesHandler",
        "📆 Calendar": "CalendarHandler",
    },
    row_width=3
)
def handle_response(handler: str):
    self.handoff(handler).handle()

self.chain.edit()
```

## `_on_handoff` Hook

When a handler is reached via `handoff()`, its `_on_handoff()` method is called automatically. Override it to run setup logic that should only happen on handoff — not on direct invocation:

```python
class ProfileHandler(telekit.Handler):

    def _on_handoff(self, origin: telekit.Handler) -> None:
        # origin is the handler that transferred control here
        self._came_from = type(origin).__name__

    def handle(self) -> None:
        self.chain.sender.set_title("👤 Profile")
        ...
```

> [!NOTE]
> If you're building reusable "back" button logic, consider the [`TrackHandoffOrigin`](./10_traits.md#trackhandofforigin) trait — it handles `_on_handoff` tracking automatically.

## Errors

| **Situation**                        | **Exception**  |
| ------------------------------------ | -------------- |
| String name not found in registry    | `NameError`    |
| Passed value is not a Handler class  | `TypeError`    |

```python
self.handoff("NonExistentHandler")  # NameError
self.handoff("not a handler")       # NameError
self.handoff(42)                    # TypeError
```

[Next: Traits »](./10_traits.md)