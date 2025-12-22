# Risk Game

```py
import telekit
import random

class StartHandler(telekit.Handler):
    @classmethod
    def init_handler(cls) -> None:
        cls.on.command("start").invoke(cls.handle)

    def handle(self):
        counter = self.get_counter()

        with self.chain.sender as s:
            s.set_title("🎰 Risk Game")
            s.set_message(
                "Press the button and take a risk.\n\n"
                "Each click:\n"
                "• either 💥 resets your score\n"
                "• or 💰 increases it\n\n"
                "Keep going until you chicken out 😉"
            )

        @self.chain.inline_keyboard({"🎲 Roll": None})
        def _(message, _value: None):
            value = counter()

            if value == 0:
                text = (
                    "💥 You lost everything.\n\n"
                    "Current score: 0\n"
                    "You can start over."
                )
            else:
                text = (
                    f"💰 Current score: {2 ** value * 100}\n\n"
                    "One more click — either more, or back to zero."
                )

            self.chain.sender.set_message(text)
            self.chain.edit()

        self.chain.set_remove_inline_keyboard(False)
        self.chain.set_remove_timeout(False)
        self.chain.set_default_timeout(120)
        self.chain.send()

    def get_counter(self):
        i = 0
        def counter():
            nonlocal i
            if i and not random.randint(0, 2):
                i = 0
            else:
                i += 1
            return i
        return counter

telekit.Server(TOKEN).polling()
```