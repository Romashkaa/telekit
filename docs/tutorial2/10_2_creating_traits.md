# Creating Traits

A trait is a plain Python class that inherits from `telekit.Trait`.
It follows the same structure as a handler — place it in a `traits/` folder alongside your `handlers/` folder.

```
my_bot/
├── handlers/
│   ├── start.py
│   └── booking.py
└── traits/
    └── confirm_step.py
```

## Minimal example

The trait below adds a reusable confirmation step to any handler.
Instead of copy-pasting "Are you sure?" logic everywhere, inherit once and call `self.ask_confirmation()`.

> `traits/confirm_step.py` file
```python
from typing import Callable

import telekit
from telekit.types import InlineKeyboard

class ConfirmStep(telekit.Trait):

    # Optional class-level config — subclasses can override these
    CONFIRM_LABEL: str = "✅ Yes"
    CANCEL_LABEL:  str = "❌ No"

    def ask_confirmation(
        self,
        text: str,
        on_confirm: Callable[[], None],
        on_cancel:  Callable[[], None] | None = None,
    ) -> None:
        """
        Display a confirmation prompt with Yes / No buttons.

        Args:
            text:       Question to show the user.
            on_confirm: Called when the user taps the confirm button.
            on_cancel:  Called when the user taps the cancel button.
                        If None, the message is simply dismissed.
        """
        self.chain.sender.set_message(text)

        self.chain.set_keyboard(
            InlineKeyboard()
                .add_callback(self.CONFIRM_LABEL, on_confirm)
                .add_callback(self.CANCEL_LABEL, on_cancel or self._default_cancel)
        )
        self.chain.edit()

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _default_cancel(self) -> None:
        self.chain.sender.set_message("Cancelled.")
        self.chain.edit()
```

Use it in a handler:

```python
from telekit.traits import ConfirmStep
import telekit


class DeleteHandler(ConfirmStep, telekit.Handler):

    CONFIRM_LABEL = "🗑️ Delete"   # override the default label
    CANCEL_LABEL  = "Keep it"

    @classmethod
    def init_handler(cls) -> None:
        cls.on.command("delete").invoke(cls.handle)

    def handle(self) -> None:
        self.chain.sender.set_title("⚠️ Delete account")
        self.ask_confirmation(
            text="This will permanently delete your account. Continue?",
            on_confirm=self._on_confirmed,
        )

    def _on_confirmed(self) -> None:
        # ... delete logic ...
        self.chain.sender.set_message("Your account has been deleted.")
        self.chain.edit()
```

## What you can use inside a Trait

Because `telekit.Trait` is part of the handler lifecycle, it has access to the same context as the handler itself:

| **Available**              | **Description**                                      |
| -------------------------- | ---------------------------------------------------- |
| `self.chain`               | The active chain (sender, keyboard, entry, timeout). |
| `self.chain.sender`        | Compose and send messages.                           |
| `self.handoff(Handler)`    | Transfer control to another handler.                 |

## Combining traits

Traits compose naturally — just list them before `telekit.Handler`:

```python
class BookingHandler(ConfirmStep, PaginatedChoice, telekit.Handler):
    ...
```

When multiple traits define the same hook (e.g. `_on_handoff`), Python's MRO applies — call `super()` to ensure all traits in the chain are notified:

```python
class MyTrait(telekit.Trait):
    def _on_handoff(self, origin: telekit.Handler) -> None:
        # your logic here
        super()._on_handoff(origin)  # always forward
```
