# Counter

Toggle Bold, Italic, Link, and Quote formatting on and off with inline buttons.

```py
import telekit
from telekit.types import InlineKeyboard, Bold, Italic, Link, Group, Quote
from telekit.traits import TrackHandoffOrigin


class StyleHandler(TrackHandoffOrigin, telekit.Handler):
    @classmethod
    def init_handler(cls) -> None:
        """
        Initializes the message handler for the '/style' command.
        """
        cls.on.command("style").invoke(cls.handle)

    DEFAULT_STYLES = {
        "bold": True,
        "italic": True,
        "link": True,
        "quote": True
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.styles = self.DEFAULT_STYLES.copy()

    def handle(self) -> None:
        do_apply_bold = self.styles["bold"]
        do_apply_italic = self.styles["italic"]
        do_apply_link = self.styles["link"]
        do_apply_quote = self.styles["quote"]

        self.chain.sender.set_text(
            Group(
                Bold("🎨 Message style settings", enabled=do_apply_bold),
                "\n\n",
                "In the Mariana Trench — the deepest point in the ocean — pressure exceeds a thousand atmospheres. ",
                Bold("Despite that", enabled=do_apply_bold),
                ", fish and mollusks live there, adapted to total darkness. ",
                Italic("Some of them glow on their own", enabled=do_apply_italic),
                " through bioluminescence. ",
                Link("Read more about the trench", url="https://en.wikipedia.org/wiki/Mariana_Trench", enabled=do_apply_link),
                ".\n\n",
                Quote(
                    "The buttons below toggle each style on and off — give it a try.",
                    enabled=do_apply_quote,
                ),
                sep="",
            )
        )
        self.chain.sender.set_link_preview_options(show_above_text=True)
        self.chain.set_keyboard(
            InlineKeyboard()
            .grid(2)
                .add_callback(self._toggle_label("bold"), self.apply, ["bold", not do_apply_bold])
                .add_callback(self._toggle_label("italic"), self.apply, ["italic", not do_apply_italic])
                .add_callback(self._toggle_label("link"), self.apply, ["link", not do_apply_link])
                .add_callback(self._toggle_label("quote"), self.apply, ["quote", not do_apply_quote])
            .grid_end()
                .add_callback("« Back", self.handoff_back, when=self.is_handed_off)
                .add_callback("↺ Reset", self.reset, when=self.styles != self.DEFAULT_STYLES)
        )
        self.chain.edit()

    def apply(self, style_name: str, new_value: bool) -> None:
        self.styles[style_name] = new_value
        self.handle()

    def reset(self) -> None:
        self.styles = self.DEFAULT_STYLES.copy()
        self.handle()

    def _toggle_label(self, style_name: str) -> str:
        icon = "✅" if self.styles[style_name] else "❌"
        return f"{icon} {style_name.capitalize()}"

TOKEN: str = telekit.utils.read_token(".env") # read token from environment
telekit.Server(TOKEN).polling()
```