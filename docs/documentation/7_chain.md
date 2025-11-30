# Chains

A `Chain` is the core element of Telekit, combining a `Sender` (View) and an `InputHandler` (Logic).
(The latter usually works “under the hood,” so you typically don’t interact with it directly)

Proper usage of a Chain is crucial for predictable bot behavior.

## Case 1 — Using the Same Chain Across All Methods

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

## Case 2 — Using Separate Chains for Each Step

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

Using a separate Chain for each step is also fine for memory usage, but it won’t provide automatic animations – you’ll need to call `chain.sender.set_edit_message(...)` yourself. 

On the plus side, it doesn’t retain any previous settings.

### By the way:

- `self.new_chain()` updates the `chain` attribute in the `handler` (`self.chain`):

```python
old = self.chain
self.new_chain()
print(old == self.chain)             # False (the "сhain" object has been replaced)

old2 = self.chain
local_chain = self.get_local_chain()
print(local_chain == self.chain)     # False ("local_chain" is local)
print(old2 == self.chain)            # True  (The "сhain" object remained)
```
