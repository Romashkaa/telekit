# Risk Game

```py
import telekit
import random

class StartHandler(telekit.Handler):
    @classmethod
    def init_handler(cls) -> None:
        cls.on.command("start").invoke(cls.handle)

    def handle(self):
        with self.chain.sender as s:
            s.set_title("🎰 Risk Game")
            s.set_message(
                "Press the button and take a risk.\n\n"
                "Each click:\n"
                "• either 💥 resets your score\n"
                "• or 💰 increases it\n\n"
                "Keep going until you chicken out 😉"
            )

        self.i = 0

        self.chain.set_inline_keyboard(
            {
                "🎲 Roll": self.roll
            }
        )

        self.chain.set_remove_inline_keyboard(False)
        self.chain.set_remove_timeout(False)
        self.chain.set_default_timeout(120)
        self.chain.send()

    def roll(self):
        value: int = self._roll()

        if value == 0:
            text: str = (
                "💥 You lost everything.\n\n"
                "Current score: 0\n"
                "You can start over."
            )
        else:
            score: int = 2 ** value * 100
            text: str = (
                f"💰 Current score: {score}\n\n"
                "One more click — either more, or back to zero."
            )

        self.chain.sender.set_message(text)
        self.chain.edit()

    def _roll(self):
        if self.i and not random.randint(0, 2):
            self.i = 0
        else:
            self.i += 1
        return self.i

telekit.Server(TOKEN).polling()
```