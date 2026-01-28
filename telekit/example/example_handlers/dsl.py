import telekit

class DSLHandler(telekit.TelekitDSL.Mixin):
    @classmethod
    def init_handler(cls) -> None:
        cls.analyze_string("""
            @ main {
                title = "📚 Telekit DSL Examples"
                message = `
                    Explore DSL examples step by step — from simple to advanced.

                    Use the buttons below to try them out:
                `
                use_italics = true;

                buttons (2) {
                    handoff("📚 FAQ", "FAQHandler")
                    handoff("🤔 Quiz", "QuizHandler")
                    handoff("🐍 Python API", "PyAPIHandler")
                    handoff("🛏️ Hotel (Simple)", "HotelHandler")
                    handoff("🏨 Hotel (Complete)", "CompleteHotelHandler")
                }
            }
        """)
        cls.on.command("dsl").invoke(cls.handle)

    def handle(self):
        self.start_script()