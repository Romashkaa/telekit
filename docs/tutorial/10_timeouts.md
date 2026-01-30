# Timeouts

Timeouts in **Telekit** allow you to control how long a chain waits for user response.
They are most commonly used together with entries and inline keyboards to limit waiting time
and handle inactive users gracefully.

## What is a timeout?

A timeout is a timer attached to a chain.  
If the user does **not** respond within the specified time, the timeout handler is executed automatically.

Typical use cases:
- Cancel inactive handlers (free memory)
- Show reminders

## When timeouts are checked

A timeout is scheduled when `chain.send()` or `chain.edit()` is called.

- If the user interacts before the timeout expires, the timeout is automatically cancelled
- If the user does nothing, the timeout callback is executed

## Basic timeout usage

You can register a timeout manually:

```python
self.chain.set_timeout(timeout_handler, seconds=30)
self.chain.send()
```

If the user does not respond within 30 seconds, `timeout_handler` is called:

```python
def timeout_handler():
    self.chain.sender.set_text("⏰ Time is up")
    self.chain.send()
```

### Using the on_timeout decorator

You can declare a timeout using a decorator:

```python
@self.chain.on_timeout(seconds=10)
def timeout_handler():
    self.chain.sender.set_text("Too slow")
    self.chain.send()
```

This is equivalent to calling `set_timeout()` manually.

### Default timeout helper

Telekit provides a built-in timeout for common inactivity cases:

```python
self.chain.set_default_timeout(seconds=90)
```

If the timeout expires, it edits the current message and appends a friendly inactivity notice.

## Lifecycle of Timeout

Every time you call:

- `chain.send()`
- `chain.edit()`

the timeout is **armed for that specific call**, executed if it expires, and **automatically removed**.

This means a timeout **runs at most once** and will **not trigger on next `send()` or `edit()`**, preventing outdated timeout logic from leaking into future messages.

### Disabling automatic timeout removal

If you want a timeout to survive multiple sends or edits:

```python
self.chain.set_remove_timeout(False)
```

Most often, timeout cleanup is disabled to avoid reconfiguring it on every step.

### Manual timeout removal

You can cancel a timeout explicitly:

```python
self.chain.remove_timeout()
```

This immediately disables the timeout.

### One timeout per chain

Only one timeout can exist per chain. Calling `set_timeout()` again replaces the previous timeout.

## Timeouts with entry handlers

Timeouts are commonly used together with entry handlers:

```python
@self.chain.entry_text()
def name_handler(message, text):
    self.chain.sender.set_text(f"Hello {text}")
    self.chain.send()

self.chain.set_timeout(lambda: print("Timeout!"), seconds=20)
self.chain.send()
```

Behavior:
- user replies → timeout is removed
- user stays silent → lambda runs

## Timeouts with inline keyboards

Timeouts also work with inline keyboards:

```python
self.chain.set_inline_keyboard({
    "Confirm": self.confirm,
    "Cancel": self.cancel,
})

self.chain.set_timeout(lambda: print("Timeout!"), seconds=15)
self.chain.send()
```

## Timeout warnings

If a chain waits for user response without a timeout, Telekit can emit a warning. This helps prevent accidental infinite waits.

You can disable warnings:
```py
self.chain.disable_timeout_warnings()
```

## Common mistakes

- Setting a timeout after `send()`
- Forgetting that `send()` clears timeouts by default

## Summary

- Timeouts limit waiting time in chains
- A timeout is scheduled on `send()` or `edit()`
- Timeouts are **single-use** unless you call `self.chain.set_remove_timeout(False)`.
- Only one timeout can exist per chain
- Timeouts are cancelled automatically on user interaction
- Examples:
    - [Append](https://github.com/Romashkaa/telekit/blob/main/docs/examples/append_method.md) - Appending messages with timeout control
    - [Risk Game](https://github.com/Romashkaa/telekit/blob/main/docs/examples/risk_game.md) - Interactive game

[Next: Handler »](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/5_handler.md)
