from telekit.styles import Sanitize
import telekit

class StartHandler(telekit.Handler):

    # ------------------------------------------
    # Initialization
    # ------------------------------------------

    @classmethod
    def init_handler(cls) -> None:
        cls.on.message(["start"]).invoke(cls.start)
    
    def start(self):
        self.chain.sender.set_title(f"👋 Welcome, {Sanitize(self.user.first_name)}!")
        self.chain.sender.set_message(
            "I can help you get started. If you're new to this bot, please, stop, get some help! 😅"
        )
        self.chain.set_inline_keyboard(
            {
                "Help": self.help
            }
        )
        self.chain.send()
    
    def help(self):
        self.handoff("HelpHandler").handle()