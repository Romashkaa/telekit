```py
import telekit

from telekit.styles import *

class OnTextHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        @cls.on.text("Name: {name}. Age: {age}")
        def _(message, name: str, age: str):
            cls(message).handle_name_age(name, age)

        @cls.on.text("My name is {name} and I am {age} years old")
        def _(message, name: str, age: str):
            cls(message).handle_name_age(name, age)

        @cls.on.text("My name is {name}")
        def _(message, name: str):
            cls(message).handle_name_age(name, None)

        @cls.on.text("I'm {age} years old")
        def _(message, age: str):
            cls(message).handle_name_age(None, age)

        cls.on.command("on_text").invoke(cls.handle)
            
    # ------------------------------------------
    # Handling Logic
    # ------------------------------------------

    def handle_name_age(self, name: str | None, age: str | None) -> None: 

        if not name: 
            name = self.user.username

        if not age:
            age = "An unknown number of"

        self.chain.sender.set_title(Composite("Hello, ", Italic(name), "!"))
        self.chain.sender.set_message(Bold(age), " years is a wonderful stage of life!")
        self.chain.send()

    # command

    def handle(self):
        self.chain.sender.set_title(f"🦻 On Text Handler")
        self.chain.sender.set_message(
            "Try sending any of these example phrases to see the handler in action:\n\n"

            f"- ", Code('Name: John. Age: 25'), "\n"
            f"- ", Code('My name is Alice and I am 30 years old'), "\n"
            f"- ", Code('My name is Romashka'), "\n"
            f"- ", Code('I\'m 18 years old'), "\n\n"
            f"The bot will respond according to the information you provide."
        )
        self.chain.edit()

telekit.Server(TOKEN).polling()
```