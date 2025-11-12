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
        cls.on.message(["start"]).invoke(cls.start)
    
    def start(self):
        self.chain.sender.set_title(f"👋 Welcome, {self.user.first_name}!")
        self.chain.sender.set_message(
            "Here you can explore some example commands to get started.\n\n"
            "Use the buttons below to try them out:"
        )
        self.chain.sender.set_photo("https://static.wikia.nocookie.net/ssb-tourney/images/d/db/Bot_CG_Art.jpg/revision/latest?cb=20151224123450")

        @self.chain.inline_keyboard(
            {
                "🧮 Counter": "/counter",
                "⌨️ Entry": "/entry",
                "📚 FAQ": "/faq",
                "📄 Pages": "/pages",
                "🦻 On Text": "/on_text",
            }, row_width=2
        )
        def handle_response(message: telebot.types.Message, command: str):
            self.simulate_user_message(command)
        
        self.chain.send()