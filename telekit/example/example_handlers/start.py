import telekit

class StartHandler(telekit.Handler):

    # ------------------------------------------
    # Initialization
    # ------------------------------------------

    @classmethod
    def init_handler(cls) -> None:
        cls.on.command("start").invoke(cls.handle)
    
    def handle(self):
        self.chain.sender.set_title(f"👋 Welcome, {self.user.first_name}!")
        self.chain.sender.set_message(
            "Here you can explore some example commands to get started.\n\n"
            "Use the buttons below to try them out:"
        )

        @self.chain.inline_keyboard(
            {
                "🧮 Counter": "CounterHandler",
                "⌨️ Entry":     "EntryHandler",
                "📚 FAQ":         "FAQHandler",
                "📄 Pages":     "PagesHandler",
                "🦻 On Text":  "OnTextHandler",
            }, row_width=[2, 1, 2]
        )
        def handle_response(message, handler: str):
            self.handoff(handler).handle()
        
        self.chain.send()