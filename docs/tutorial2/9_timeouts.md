## Timeouts

As mentioned in the [inline keyboards](./7_inline_keyboards.md#label-callback-keyboard) section: they, along with [entries](./8_entries.md), wait for a user response forever — which is almost never a good idea, unless you're building a bot for personal use.

To let your bot recognize inactivity and free up resources, use timeouts.

### `set_default_timeout`

The simplest option is `set_default_timeout`. It automatically closes the session after the specified period of inactivity: appends a message to the current one and clears all active handlers.

```py
def update_count(self, value: int):
    self.click_count += value
    self.chain.sender.set_message(f"You clicked {self.click_count} times")

    self.chain.set_default_timeout(5)
    
    self.chain.edit()
```

> full code [here](../examples/counter.md)

By default, the user will see `"Looks like things went quiet... See you next time!"`, but you can customize it:

```py
self.chain.set_default_timeout(60, message=Group("Session expired. Send ", Code("/start"), " to begin again."))
```

### `set_timeout` and `@on_timeout`

If you need custom logic on timeout — use `set_timeout` or the `@chain.on_timeout` decorator:

```py
def handle_name(self) -> None:
    self.chain.sender.set_text("What's your name?")
    self.chain.set_entry_text(self.handle_name_response)

    self.chain.set_timeout(self.handle_timeout, seconds=30)
    
    self.chain.send()

def handle_timeout(self) -> None:
    self.chain.sender.set_text("Timed out. Send /start to try again.")
    self.chain.send()
```

Or with the decorator:

```py
@chain.on_timeout(minutes=1)
def my_timeout():
    self.chain.sender.set_text("Where did you go?")
    self.chain.send()
```

> [!NOTE]
> If an entry or inline keyboard is active but no timeout is set, the bot will print a warning to the console — a reminder that the session may hang indefinitely. This behavior is controlled by `telekit.debug.Debug.timeout_warnings` and is disabled by default.

[Traits](10_traits.md)