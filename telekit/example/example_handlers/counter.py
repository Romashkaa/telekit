import telekit
from telekit.types import ButtonStyle, CallbackButton

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

    def handle(self) -> None:
        self.chain.sender.set_title("Hello")
        self.chain.sender.set_message("Click the button below to start interacting")
        self.chain.sender.set_photo("https://static.wikia.nocookie.net/ssb-tourney/images/d/db/Bot_CG_Art.jpg/revision/latest?cb=20151224123450")
        self.chain.sender.set_effect(self.chain.sender.Effect.PARTY)

        self.click_count = 0

        self.chain.set_inline_keyboard(
            {
                "⊖": CallbackButton(self.update_count, [-1], style=ButtonStyle.DANGER),
                "⊕": CallbackButton(self.update_count, [1], style=ButtonStyle.SUCCESS),
            }, row_width=2
        )
            
        self.chain.set_remove_inline_keyboard(False)
        self.chain.disable_timeout_warnings()
        self.chain.edit()

    def update_count(self, value: int):
        self.click_count += value
        self.chain.sender.set_message(f"You clicked {self.click_count} times")
        self.chain.edit()