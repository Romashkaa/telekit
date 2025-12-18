# Dialogue

```python
import telebot.types
import telekit

class DialogueHandler(telekit.Handler):

    # ------------------------------------------
    # Initialization
    # ------------------------------------------

    @classmethod
    def init_handler(cls) -> None:
        @cls.on.text("Hello!", "hello!", "Hello", "hello")
        def _(message: telebot.types.Message):
            cls(message).handle_hello()

    # ------------------------------------------
    # Handling Logic
    # ------------------------------------------

    def handle_hello(self) -> None:
        self.chain.sender.set_text("👋 Hello! What is your name?")

        @self.chain.entry_text()
        def _(message: telebot.types.Message, name: str):
            self.handle_name(name)
            
        self.chain.send()

    def handle_name(self, name: str):
        self._user_name: str = name

        self.chain.sender.set_text(f"Nice! How are you?")

        @self.chain.entry_text()
        def _(message, feeling: str):
            self.handle_feeling(feeling)

        self.chain.send()

    def handle_feeling(self, feeling: str):
        self.chain.sender.set_text(f"Got it, {self._user_name.title()}! You feel: {feeling}")
        self.chain.send()

telekit.Server(TOKEN).polling()
```