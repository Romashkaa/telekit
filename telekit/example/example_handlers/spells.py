import telekit

from telekit.inline_buttons import CallbackButton

spells_text = """
# Expelliarmus

The Disarming Charm. It causes whatever the victim is holding to fly out of their hand. It became Harry Potter's signature spell.

# Wingardium Leviosa

The Levitation Charm. Used to make objects fly. As Hermione Granger famously noted, it's "Levi-o-sa, not Levio-sar."

# Expecto Patronum

The Patronus Charm. A highly advanced spell that conjures a silver guardian to protect the caster against Dementors.

# Alohomora

The Unlocking Charm. Used to open doors and windows that are not protected by magic.

# Lumos

The Wand-Lighting Charm. Illuminates the tip of the caster's wand, allowing them to see in the dark.
"""

spells: dict[str, str] = {}

for title, content in telekit.chapters.parse(spells_text).items():
    spells[title] = content

class SpellsHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        cls.on.command("spells").invoke(cls.handle)

    # ------------------------------------------
    # Handling Logic
    # ------------------------------------------

    def handle(self) -> None:
        self.display_home_page()

    def display_home_page(self) -> None:
        self.chain.sender.set_title("📜 Wizarding Library")
        self.chain.sender.set_message("Select a spell from the list below to see its description:")

        self.chain.set_inline_keyboard(
            {
                title: CallbackButton(self.display_home_page, answer_text=content) 
                for title, content in spells.items()
            }
        )
        self.chain.set_remove_inline_keyboard(False)

        self.chain.disable_timeout_warnings()
        self.chain.edit()