# Command Parameters

```py
import telekit
from telekit.parameters import Int, Str
from telekit.styles import Sanitize, Code

class StartHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        #                                    ↓ value to return if conversion fails
        cls.on.command("start", params=[Int(-1), Str()]).invoke(cls.handle)
    
    def handle(self, age: int | None=None, name: str | None=None):
        if age is None:
            self.chain.sender.set_text("Info is missing. Please provide your age and name:\n\n", Code("/start 21 Lois"))
        elif age == -1:
            self.chain.sender.set_text("Invalid age provided. Please enter a valid number:\n\n", Code(f"/start 21 \"Lois Lane\""))
        elif name is None:
            self.chain.sender.set_text("Name is missing. Please provide your name:\n\n", Code(f"/start {age} \"Lois Lane\""))
        else:
            self.chain.sender.set_text(f"Hey {Sanitize(name)}! {age} years already? Time flies, huh 😅")

        self.chain.sender.set_parse_mode("html")
        self.chain.send()

telekit.Server(TOKEN).polling()
```

# Deep Link: Invite Code

```py
import telekit
from telekit.styles import BotLink
from telekit.parameters import Str

class StartHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        # one string parameter from deep link
        cls.on.command("start", params=[Str()]).invoke(cls.handle)
    
    def handle(self, invite_code: str | None = None):
        if invite_code is None:
            self.chain.sender.set_text("This link is missing an invite code.")
        else:
            self.chain.sender.set_text(
                f"You joined via invite code: {invite_code}\n\n",
                BotLink("Invite your friends too!", username=self.bot.get_me().username, start=invite_code)
            )

        self.chain.sender.set_reply_to(self.message) # reply to user's message
        self.chain.sender.set_parse_mode("html")
        self.chain.send()

telekit.Server(TOKEN).polling()
```