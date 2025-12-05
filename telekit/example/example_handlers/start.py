import telebot.types
import telekit
import typing


class StartHandler(telekit.Handler):

    # ------------------------------------------
    # Initialization
    # ------------------------------------------

    @classmethod
    def init_handler(cls) -> None:
        """
        Initializes the message handler for the '/start' command.
        """
        cls.on.command("start").invoke(cls.handle)
    
    def handle(self):
        self.chain.sender.set_title(f"👋 Welcome, {self.user.first_name}!")
        self.chain.sender.set_message(
            "Here you can explore some example commands to get started.\n\n"
            "Use the buttons below to try them out:"
        )
        # self.chain.sender.set_photo("https://static.wikia.nocookie.net/ssb-tourney/images/d/db/Bot_CG_Art.jpg/revision/latest?cb=20151224123450")

        @self.chain.inline_keyboard(
            {
                "🧮 Counter": "CounterHandler",
                "⌨️ Entry":     "EntryHandler",
                "📚 FAQ":         "FAQHandler",
                "📄 Pages":     "PagesHandler",
                "🦻 On Text":  "OnTextHandler",
            }, row_width=2
        )
        def handle_response(message: telebot.types.Message, handler: str):
            self.handoff(handler).handle() # type: ignore
        
        self.chain.send()