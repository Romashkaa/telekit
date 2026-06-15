import telekit
from telekit.types import InlineKeyboard, ButtonStyle

class CounterHandler(telekit.Handler):

    # ------------------------------------------
    # Initialization
    # ------------------------------------------

    @classmethod
    def init_handler(cls) -> None:
        """
        Initializes the message handler for the '/counter' command.
        """
        cls.on.command("counter").invoke(cls.handle)

    # ------------------------------------------
    # Handling Logic
    # ------------------------------------------

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.click_count = 0

    def handle(self, value: int = 0) -> None:
        self.click_count += value

        self.chain.sender.set_title("Hello")
        self.chain.sender.set_message(
            f"You clicked {self.click_count} times"
                if self.click_count else
            "Click the button below to start interacting"
        )
        self.chain.sender.set_photo("https://static.wikia.nocookie.net/ssb-tourney/images/d/db/Bot_CG_Art.jpg/revision/latest?cb=20151224123450")
        self.chain.sender.set_effect(self.chain.sender.Effect.PARTY)

        self.chain.set_keyboard(
            InlineKeyboard()
                .add_callback("⊖", self.handle, [-1], when=self.click_count, style=ButtonStyle.DANGER)
                .add_callback("⊕", self.handle, [1], style=ButtonStyle.SUCCESS)
            .row()
                .add_callback("↺ Reset", self.reset_counter, when=self.click_count)
        )

        self.chain.edit()

    def reset_counter(self):
        self.click_count = 0
        self.handle()