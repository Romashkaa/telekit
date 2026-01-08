# Jinja Engine

```py
import telekit

class HotelHandler(telekit.TelekitDSL.Mixin):

    @classmethod
    def init_handler(cls) -> None:
        cls.on.command("start").invoke(cls.handle)
        cls.analyze_source(script)

    def handle(self):
        # optional: add runtime data to Jinja
        self.set_jinja_context(
            hotel_name="Romashka Hotel",
            rooms=["Economy", "Comfort", "Luxury"]
        )
        self.start_script()


script = """
$ {
    template = "jinja"
}

@ main {
    title = "🏨 Welcome to {{ hotel_name }}!"
    message = `
        Hello, {{ handler.user.first_name or "guest" | e }} 👋

        Available room types:
        {% for room in rooms -%}
        • {{ room }}
        {% endfor %}
        Please choose an option below
    `
    parse_mode = "markdown"
}
"""

telekit.Server(BOT_TOKEN).polling()
```