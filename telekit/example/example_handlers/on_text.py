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
            cls(message).handle(name, age)

        @cls.on.text("My name is {name} and I am {age} years old")
        def _(message: telebot.types.Message, name: str, age: str):
            cls(message).handle(name, age)

        @cls.on.text("My name is {name}")
        def _(message: telebot.types.Message, name: str):
            cls(message).handle(name, None)

        @cls.on.text("I'm {age}  years old")
        def _(message: telebot.types.Message, age: str):
            cls(message).handle(None, age)
            
    # ------------------------------------------
    # Handling Logic
    # ------------------------------------------

    def handle(self, name: str | None, age: str | None) -> None: 

        if not name: 
            name = self.user.get_username()

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

        self.chain.sender.set_title(f"Hello {styles.italic(name)}!")
        self.chain.sender.set_message(
            f"{styles.bold(age)} years is a wonderful stage of life!\n" 
            f"{styles.quote(f'(You can customize styles)')}"
        )
        self.chain.send()
