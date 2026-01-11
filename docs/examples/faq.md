# FAQ (Telekit DSL)

```py
import telekit

class FAQHandler(telekit.TelekitDSL.Mixin):
    @classmethod
    def init_handler(cls) -> None:
        cls.analyze_source(script)
        cls.on.command("faq").invoke(cls.start_script)

# ------------------------------------------------------
# Telekit DSL
# ------------------------------------------------------
#
# Tutorial on GitHub: https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/11_telekit_dsl.md
#

script = """
@ main {
    title   = "📖 FAQ - Frequently Asked Questions"
    message = "Here are answers to common questions to help you get started:"

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
        back(); pricing("Pricing »")
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
        back(); contact("Contact »")
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

telekit.Server(TOKEN).polling()
```