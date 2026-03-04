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
                "🧮 Counter":            "CounterHandler",
                "🧙‍♀️ Spells":              "SpellsHandler",
                "⌨️ Entry":                "EntryHandler",

                "📚 Telekit DSL Examples":   "DSLExampleHandler",
                
                "📖 Pages":                "PagesHandler",
                "🦻 On Text":             "OnTextHandler",
                "📄 File Info":     "TextDocumentHandler",
                
                "🖼️ QR Editor":               "QRHandler",
            }, row_width=[3, 1, 3, 1]
        )
        def handle_response(handler: str):
            self.handoff(handler).handle()
        
        self.chain.disable_timeout_warnings()
        self.chain.edit()