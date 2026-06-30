import telekit
from telekit.types import InlineKeyboard, ButtonStyle, Bold, Group, Quote, TextBuilder
from telekit.utils import CyclicList
from telekit.traits import TrackHandoffOrigin

class CounterHandler(TrackHandoffOrigin, telekit.Handler):

    # ------------------------------------------
    # Initialization
    # ------------------------------------------

    @classmethod
    def init_handler(cls) -> None:
        """
        Initializes the message handler for the '/counter' command.
        """
        cls.on.command("counter").invoke(cls.handle)

    # ------------------------------------------
    # Handling Logic
    # ------------------------------------------

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.click_count = 0

    def handle(self, value: int = 0) -> None:
        self.click_count += value

        show_tip: bool = self.click_count > 3

        self.chain.sender.set_title("👋 Hello!")
        self.chain.sender.set_message(
            TextBuilder()
            .if_(self.click_count)
                .if_(show_tip)
                    .add_group("Telekit says", Bold("#", self.click_count), sep=" ")
                    .newln()
                    .add_quote(GUIDELINES[self.click_count - 4])
                .else_()
                    .add_group("You clicked", Bold(self.click_count), "times.", sep=" ")
                    .spacer(when=self.click_count > 1)
                    .add_bold("💡 Keep clicking to see the tips", when=self.click_count > 1)
                .endif()
            .else_()
                .add("Click the button below to start interacting")
            .endif()
        )
        self.chain.sender.set_photo("https://static.wikia.nocookie.net/ssb-tourney/images/d/db/Bot_CG_Art.jpg/revision/latest?cb=20151224123450")
        self.chain.sender.set_effect(self.chain.sender.Effect.PARTY)

        self.chain.set_keyboard(
            InlineKeyboard()
                .add_callback("« Back", self.handoff_back, when=self.is_handed_off and not self.click_count)
                .add_callback("⊖", self.handle, [-1], when=self.click_count, style=ButtonStyle.DANGER)
                .add_callback("⊕", self.handle, [1], style=ButtonStyle.SUCCESS)
            .row()
                .add_callback("↺ Reset", self.reset_counter, when=self.click_count)
        )

        self.chain.edit()

    def reset_counter(self):
        self.click_count = 0
        self.handle()

GUIDELINES = CyclicList(
    "Keep the style consistent across the bot — don't change the approach from screen to screen.",
    "Predictability matters more than originality: the user shouldn't have to guess what happens after pressing a button.",
    "Use the 'title + body' format: the title gives orientation, the body reveals the details.",
    "Bold is for the most important things. Don't bold more than 20% of the text.",
    "`code` is only for technical values: commands, variables, tokens.",
    "Embed links into text with a label, not as a raw URL.",
    "Emoji at the start of a line works as a section icon — it's clean and reads fast.",
    "Don't place emoji in the middle of a sentence — it breaks the reading flow.",
    "One or two emoji per message is enough. More is noise.",
    "Button labels should be actions, not states. 'Cancel' instead of 'Cancellation'.",
    "Don't put more than 2–3 buttons in one row — they become unreadable on mobile.",
    "Don't send multiple messages in a row when one will do.",
    "If an action is no longer available — hide the button, don't leave it inactive without explanation.",
    "Use a title for navigation: the user should understand where they are in the bot.",
    "A blank line between logical blocks is a simple way to make a message look cleaner.",
)