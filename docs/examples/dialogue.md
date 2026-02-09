# Dialogue

```python
import telekit

class DialogueHandler(telekit.Handler):

    # ------------------------------------------
    # Initialization
    # ------------------------------------------

    @classmethod
    def init_handler(cls) -> None:
        cls.on.regexp(
            r'\b(hello|hi|hey|привіт|вітаю|добрий день|добридень|ку)\b'
        ).invoke(cls.handle_hello)

    # ------------------------------------------
    # Handling Logic
    # ------------------------------------------

    def handle_hello(self) -> None:
        self.chain.sender.set_text("👋 Hello! What is your name?")
        self.chain.set_entry_text(self.handle_name)
            
        self.chain.send()

    def handle_name(self, name: str):
        self.name: str = name

        self.chain.sender.set_text(f"Nice! How are you?")
        self.chain.set_entry_text(self.handle_feeling)

        self.chain.send()

    def handle_feeling(self, feeling: str):
        self.chain.sender.set_text(f"Got it, {self.name.title()}! You feel: {feeling}")
        self.chain.send()

telekit.Server(TOKEN).polling()
```