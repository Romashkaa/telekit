import telekit

from telekit.styles import Bold
from telekit.types import InlineKeyboard


class StartHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        cls.on.command("start").invoke(cls.handle)

    def handle(self):
        self.chain.sender.set_title(f"👋 Welcome, {self.user.first_name}!")
        self.chain.sender.set_message(
            "Ready to build something with Telekit?",
            "\n\n",
            Bold("New project? Let's get everything set up")
        )

        self.chain.set_keyboard(
            InlineKeyboard()
            .grid(1)
                .add_alert(
                    "💿 Install Telekit",
                    "Not yet? No worries! Run `pip install telekit` "
                    "or `pip install -r requirements.txt` to get started."
                )
                .add_alert(
                    "🤐 Set up .env",
                    "Create a `.env` file and add your bot token like this:\n\n"
                    "`TOKEN=your_bot_token_here`"
                )
            .grid(2)
                .add_link(
                    "✨ Examples",
                    "https://github.com/Romashkaa/telekit/blob/main/docs/examples/examples.md"
                )
                .add_link(
                    "🧑‍🏫 Tutorial",
                    "https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/0_tutorial.md"
                )
        )

        self.chain.edit()