# FAQ (Telekit DSL)

This example demonstrates how to build a simple multi-scene FAQ using **Telekit DSL**.

> `main.py`

The handler analyzes the DSL script, registers the `/faq` command, and starts the script
from the "main" scene.

```py
import telekit

class FAQHandler(telekit.TelekitDSL.Mixin):
    @classmethod
    def init_handler(cls) -> None:
        cls.analyze_file("script.scr")
        cls.on.command("faq").invoke(cls.start_script)

telekit.Server(TOKEN).polling()
```

> `script.scr`

The script is loaded once and executed starting from the `@ main` scene when the `/faq`
command is triggered.

```js
@ main {
    title   = "📖 FAQ – Frequently Asked Questions"
    message = "Here are answers to common questions to help you get started."

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
        - Mobile Applications
        - Cloud Solutions
        - IT Consulting
    `

    buttons (2) {
        back()
        pricing("Pricing »")
    }
}

@ pricing {
    title   = "💰 Pricing & Plans"
    message = `
        We offer flexible pricing options:
        - Basic — $99 / month
        - Pro — $199 / month
        - Enterprise — Custom pricing
    `

    buttons (2) {
        back()
        contact("Contact »")
    }
}

@ contact {
    title   = "📞 Contact & Support"
    message = `
        For inquiries, partnerships, or support:
        - Email: support@company.com
        - Telegram: @CompanySupportBot
    `

    buttons {
        back()
    }
}
```

### Notes

- Each block prefixed with `@` defines a **scene**
- `title` + `message` is the recommended layout for structured content
- `buttons` define navigation between scenes
- `back()` automatically returns to the previous scene

> [!TIP]
> For a complete overview of the Telekit DSL syntax, including scenes, attributes and buttons, see the [Telekit DSL Syntax tutorial](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md)
