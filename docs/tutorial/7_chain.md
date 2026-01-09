# Chains

A `Chain` is the core element of Telekit, combining a `Sender` (View) and an `InputHandler` (Logic).
(The latter usually works “under the hood,” so you typically don’t interact with it directly)

Proper usage of a Chain is crucial for predictable bot behavior.

## Using the Same Chain

In this approach, the same Chain instance is used throughout all methods of the class:

```python
class MyHandler(telekit.Handler):
    ...
    def first(self) -> None:
        self.chain.sender.set_text("1st page")
        self.chain.set_inline_keyboard(
            {
                "Next": self.second
            }
        )
        self.chain.edit()

    def second(self) -> None:
        self.chain.sender.set_text("2nd page")
        self.chain.set_inline_keyboard(
            {
                "Back": self.first
            }
        )
        self.chain.edit()
```

Using the same `Chain` can help save memory and automatically replaces the previous message with smooth animations. However, it also retains some previous settings.

## Using Separate Chains

In this approach, a new Chain instance is created for each step:

```python
class MyHandler(telekit.Handler):
    ...
    def first(self) -> None:
        chain = self.get_local_chain()
        chain.sender.set_text("1st page")
        chain.set_inline_keyboard(
            {
                "Next": self.second
            }
        )
        chain.edit()

    def second(self) -> None:
        chain = self.get_local_chain()
        chain.sender.set_text("2nd page")
        chain.set_inline_keyboard(
            {
                "Back": self.first
            }
        )
        chain.edit()
```

Using a separate Chain for each step is also fine for memory usage, but it won’t provide automatic animations – you’ll need to call `chain.sender.set_edit_message(...)` yourself. Also it doesn’t retain any previous settings.

## Additional notes

- `new_chain()` creates a new `Chain` instance and assigns it to the handler.
  This means the `self.chain` attribute is replaced with a new object:

```python
old = self.chain
self.new_chain()
print(old == self.chain)  # False — the previous Chain instance was replaced
```

- `get_local_chain()` returns a new `Chain` instance **without** modifying the handler's current chain.
  The original `self.chain` remains unchanged, while the returned chain is fully independent:

```python
old = self.chain
local_chain = self.get_local_chain()

print(old == self.chain)         # True  — the handler’s Chain was not changed
print(local_chain == self.chain) # False — the local Chain is a separate instance
```

In practice, use `new_chain()` when you want to reset the handler’s chain state entirely.
Use `get_local_chain()` when you need a temporary or isolated Chain for a single action,
without affecting the handler’s main Chain.

## Attribute Cleanup

Each time `.send()` or `.edit()` is called, the chain **automatically clears** its state:
- timeouts
- entry handlers 
- inline keyboards

This behavior ensures predictability between steps.

### Disabling automatic cleanup

You can selectively disable this behavior (`chain.*`):

- `set_remove_timeout(False)`
- `set_remove_entry_handler(False)`
- `set_remove_inline_keyboard(False)`

Most often, timeout cleanup is disabled to avoid reconfiguring it on every step.

### Manual cleanup

You can also clear handlers explicitly:

```python
self.chain.remove_timeout()
self.chain.remove_entry_handler()
self.chain.remove_inline_keyboard()
```

Or remove **all handlers at once**:

- `self.chain.remove_all_handlers()` — forcibly removes all handlers associated with the chain.

[Next: Timeouts »](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/10_timeouts.md)