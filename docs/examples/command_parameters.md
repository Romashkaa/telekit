# Command Parameters

```py
import telekit
from telekit.parameters import Int, Str

class StartHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        # Define parameters: first an integer, then a string
        cls.on.command("start", params=[Int(-1), Str()]).invoke(cls.handle)
    
    # Default values are required:   ↓↓↓↓                   ↓↓↓↓
    def handle(self, age: int | None=None, name: str | None=None):
        if age is None or name is None:
            self.chain.sender.set_text("Please provide your age and name.")
        elif age == -1:
            self.chain.sender.set_text("Invalid age provided.")
        else:
            self.chain.sender.set_text(f"Hello {name}! You are {age} years old.")
        
        self.chain.send()

telekit.Server(TOKEN).polling()
```

# Deep Link: Invite Code

```py
import telekit
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
            self.chain.sender.set_text(f"You joined via invite code: {invite_code}")

        self.chain.send()

telekit.Server(TOKEN).polling()
```

> [!TIP]
> Check out [documentation](../tutorial2/command_trigger_parameters.md)