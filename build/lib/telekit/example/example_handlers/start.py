import telebot.types # type: ignore
import telekit
import typing


class StartHandler(telekit.Handler):

    # ------------------------------------------
    # Initialization
    # ------------------------------------------

    @classmethod
    def init_handler(cls, bot: telebot.TeleBot) -> None:
        """
        Initializes the message handler for the '/start' command.
        """
        @bot.message_handler(commands=['start']) # type: ignore
        def handler(message: telebot.types.Message) -> None: # type: ignore
            cls(message).handle()

    # ------------------------------------------
    # Handling Logic
    # ------------------------------------------

    def handle(self) -> None:
        chain: telekit.Chain = self.get_chain()
         
        chain.sender.set_title("Hello")
        chain.sender.set_message("Welcome to the bot! Click the button below to start interacting.")
        chain.sender.set_photo("https://static.wikia.nocookie.net/ssb-tourney/images/d/db/Bot_CG_Art.jpg/revision/latest?cb=20151224123450")
        chain.sender.set_effect(chain.sender.Effect.PARTY)

        def counter_factory() -> typing.Callable[[int], int]:
            count = 0
            def counter(value: int=1) -> int:
                nonlocal count
                count += value
                return count
            return counter
        
        click_counter = counter_factory()

        @chain.inline_keyboard({"⊕": 1, "⊖": -1}, row_width=2)
        def _(message: telebot.types.Message, value: int) -> None:
            chain.sender.set_message(f"You clicked {click_counter(value)} times")
            chain.edit_previous_message()
            chain.send()

        chain.send()