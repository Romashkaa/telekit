# Append method + Timeout

```py
import telekit

from telekit.styles import Group, Sanitize, Quote

class StartHandler(telekit.Handler):
    @classmethod
    def init_handler(cls) -> None:
        cls.on.command("start").invoke(cls.start)

    def start(self):
        self.chars = iter("ROMASHKA")

        self.chain.sender.set_title(Group("Hello, ", Sanitize(self.user.first_name), "!"))
        self.chain.sender.set_message(
            "Quote of the Day:\n",
            Quote("The only way out is through."),
            "- "
        )
        self.chain.set_timeout(self.update, 1)
        self.chain.send()

    def update(self):
        char = next(self.chars, None)

        if not char:
            return
        
        self.chain.set_timeout(self.update, 1)
        self.chain.sender.append(f"{char}")    # HERE
        self.chain.edit()

telekit.Server(TOKEN).polling()
```