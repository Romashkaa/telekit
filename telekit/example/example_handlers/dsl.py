import telekit

class DSLHandler(telekit.Handler):

    # ------------------------------------------
    # Initialization
    # ------------------------------------------

    @classmethod
    def init_handler(cls) -> None:
        cls.on.command("dsl").invoke(cls.handle)
    
    def handle(self):
        self.chain.sender.set_title("📚 Telekit DSL Examples")
        self.chain.sender.set_message(
            "Explore DSL examples step by step — from simple to advanced.\n\n"
            "Use the buttons below to try them out."
        )

        @self.chain.inline_keyboard(
            {
                "📚 FAQ":             "FAQHandler",
                "🤔 Quiz":           "QuizHandler",
                "🐍 Python API":    "PyAPIHandler",
                "🏨 Hotel Booking": "HotelHandler",

                "« Back": "StartHandler"
            }, row_width=2
        )
        def handle_response(message, handler: str):
            self.handoff(handler).handle()
        
        self.chain.edit()