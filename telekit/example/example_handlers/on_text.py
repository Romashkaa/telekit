import telebot.types # type: ignore
import telekit

from telekit.buildtext import Styles
from telekit.buildtext.styles import *

class OnTextHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        """
        Initializes the message handlers.
        """
        @cls.on.text("Name: {name}. Age: {age}")
        def _(message: telebot.types.Message, name: str, age: str):
            cls(message).handle_name_age(name, age)

        @cls.on.text("My name is {name} and I am {age} years old")
        def _(message: telebot.types.Message, name: str, age: str):
            cls(message).handle_name_age(name, age)

        @cls.on.text("My name is {name}")
        def _(message: telebot.types.Message, name: str):
            cls(message).handle_name_age(name, None)

        @cls.on.text("I'm {age} years old")
        def _(message: telebot.types.Message, age: str):
            cls(message).handle_name_age(None, age)

        cls.on.message(["on_text"]).invoke(cls.handle)
            
    # ------------------------------------------
    # Handling Logic
    # ------------------------------------------

    def handle_name_age(self, name: str | None, age: str | None) -> None: 

        if not name: 
            name = self.user.username

        if not age:
            age = "An unknown number of"

        # Manually:
        # styles = Styles()
        # styles.use_html()
        # styles.set_parse_mode("markdown")

        # Automatically detects `parse_mode` according to the `sender`
        styles = self.chain.sender.styles

        # Another ways:
        # print(Bold(age).markdown)
        # print(Bold(age, parse_mode="html"))

        # Composition:
        #   Strikethrough(Bold("...") + Italic("..."))
        #   styles.strike(styles.bold("...") + styles.italic())

        self.chain.sender.set_title(styles.group("Hello, ", styles.italic(name), "!"))
        self.chain.sender.set_message(
            styles.bold(age), " years is a wonderful stage of life!\n", 
            styles.quote('(You can customize styles using "sender.styles.*")')
        )
        self.chain.send()

    # command

    def handle(self):
        code = self.chain.sender.styles.code
        self.chain.sender.set_title(f"🦻 On Text Handler")
        self.chain.sender.set_message(
            "Try sending any of these example phrases to see the handler in action:\n\n"

            f"- ", code('Name: John. Age: 25'), "\n"
            f"- ", code('My name is Alice and I am 30 years old'), "\n"
            f"- ", code('My name is Romashka'), "\n"
            f"- ", code('I\'m 18 years old'), "\n\n"
            f"The bot will respond according to the information you provide."
        )
        self.chain.edit()