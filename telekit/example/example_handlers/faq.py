import random

import telekit

class FAQHandler(telekit.TelekitDSL.Mixin):
    @classmethod
    def init_handler(cls) -> None:
        cls.on.message(commands=["faq"]).invoke(cls.start_script)
        cls.analyze_source(guide)
        
        # cls.display_script_data() # see the ast of the script

    def handle(self) -> None:
        self.start_script()

    def get_variable(self, name: str) -> str | None:
        match name:
            case "random_lose_phrase":
                phrases = [
                    "Keep going, you're doing great!",
                    "Don't give up!",
                    "Almost there, try again!",
                ]
                return random.choice(phrases)
            case _:
                # fallback to built-in variables if None
                return None

# ------------------------------------------------------
# Telekit DSL
# ------------------------------------------------------
#
# Tutorial on GitHub: https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/11_telekit_dsl.md
#

guide = """
$ timeout {
    time = 32 // seconds
}

@ main {
    title   = "🏢 Company FAQ"
    message = `
        Welcome! Select a topic to learn more about our company:
    `

    buttons {
        services("Our Services")
        pricing("Pricing & Plans")
        contact("Contact & Support")
    }
}

@ services {
    title   = "💼 Our Services"
    message = `
        We provide the following services:
        - Web Development
        - Mobile Apps
        - Cloud Solutions
        - IT Consulting
    `

    buttons (2) {
        back, pricing("Pricing »")
    }
}

@ pricing {
    title   = "💰 Pricing & Plans"
    message = `
        We offer flexible pricing plans:
        - Basic: $99/month
        - Pro: $199/month
        - Enterprise: Custom pricing
    `

    buttons (2) {
        back, contact("Contact »")
    }
}

@ contact {
    title   = "📞 Contact & Support"
    message = `
        For inquiries, partnerships, or support, contact us:
        - Email: support@company.com
        - Telegram: @CompanySupportBot
    `

    buttons { back }
}
"""
