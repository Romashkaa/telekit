![TeleKit](https://github.com/Romashkaa/images/blob/main/TeleKitWide.png?raw=true)

[![PyPI](https://img.shields.io/pypi/v/telekit.svg)](https://pypi.org/project/telekit/)
[![Python](https://img.shields.io/pypi/pyversions/telekit.svg)](https://pypi.org/project/telekit/)

# Telekit

**Telekit** is a declarative, developer-friendly library for building Telegram bots. It gives developers a dedicated Sender for composing and sending messages and a Chain for handling dialogue between the user and the bot. The library also handles inline keyboards and callback routing automatically, letting you focus on the bot's behavior instead of repetitive tasks.

```py
import telekit

class MyStartHandler(telekit.Handler):
    @classmethod
    def init_handler(cls):
        cls.on.command('start').invoke(cls.handle_start)

    def handle_start(self):
        self.chain.sender.set_text("Hello!")
        self.chain.sender.set_photo("robot.png")
        self.chain.send()

telekit.Server("BOT_TOKEN").polling()
```

> Send "Hello!" with a photo on `/start`

Telekit comes with a [built-in DSL](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/11_telekit_dsl.md), allowing developers to create fully interactive bots with minimal code. It also integrates **Jinja**, giving you loops, conditionals, expressions, and filters to generate dynamic content.

```js
@ main {
    title   = "🎉 Fun Facts Quiz";
    message = "Test your knowledge with 10 fun questions!";

    buttons {
        question_1("Start Quiz");
    }
}
```

> See the [full example](https://github.com/Romashkaa/telekit/blob/main/docs/examples/quiz.md)

Even in its beta stage, Telekit accelerates bot development, offering typed command parameters, text styling via `Bold()`, `Italic()`, built-in emoji game results for `🎲 🎯 🏀 ⚽ 🎳 🎰`, and much more out of the box. Its declarative design makes bots easier to read, maintain, and extend.

**Key features:**  
- Declarative bot logic with **chains** for effortless handling of complex conversations
- [Ready-to-use DSL](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/11_telekit_dsl.md) for FAQs and other interactive scripts
- Automatic handling of [message formatting](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/6_styles.md) via [Sender](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/5_senders.md) and **callback routing**
- **Deep Linking** support with type-checked [Command Parameters](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/command_trigger_parameters.md) for flexible user input
- Built-in **Permission** and **Logging** system for user management
- Seamless integration with [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI)
- Fast to develop and easy-to-extend code

[GitHub](https://github.com/Romashkaa/telekit)
[PyPi](https://pypi.org/project/telekit/)
[Telegram](https://t.me/NotRomashka)
[Community](https://t.me/+wu-dFrOBFIwyNzc0)

## Contents

- 🌟 [Tutorial](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/0_tutorial.md)
- 🎆 [Gallery](https://github.com/Romashkaa/telekit/blob/main/docs/documentation/gallery.md)
- 👀 [Examples](https://github.com/Romashkaa/telekit/blob/main/docs/examples/examples.md)
    - [Dialogue](https://github.com/Romashkaa/telekit/blob/main/docs/examples/dialogue.md)
    - [Risk Game](https://github.com/Romashkaa/telekit/blob/main/docs/examples/risk_game.md)
    - [Counter](https://github.com/Romashkaa/telekit/blob/main/docs/examples/counter.md)
    - [Quiz (Telekit DSL)](https://github.com/Romashkaa/telekit/blob/main/docs/examples/quiz.md)
    - [More...](https://github.com/Romashkaa/telekit/blob/main/docs/examples/examples.md)

## Overview

**Telekit** is a framework for building Telegram bots where dialogs look like normal method calls. No bulky state machines. No scattered handlers.

The idea is simple: you point to the next step — Telekit calls it when the user replies.

### Entries

No state machines. Just tell Telekit which method should handle the next user message.

```py
def handle(self):
    self.chain.sender.set_text("👋 Hello! What is your name?")
    self.chain.set_entry_text(self.handle_name)
    self.chain.send()

def handle_name(self, name: str):
    self.chain.sender.set_text(f"Nice to meet you, {name}!")
    self.chain.send()
```


The `handle` method sends a message and registers `handle_name` as the next step using `set_entry_text`.

When the user replies, Telekit automatically calls `handle_name` and passes the user's message as a plain `str` argument.

That's it. No enums. No manual state tracking. No boilerplate.

### Inline Keyboards

Buttons can either **return a value** or **call a method directly**.

**Choice keyboard** — map button labels to values. The selected value is passed straight into your handler:

```py
self.chain.set_inline_choice(
    self.on_choice,
    choices={
        "Option 1": "Value 1",
        "Option 2": "Value 2",
        "Option 3": [3, "Yes, it's an array"],
    }
)

def on_choice(self, choice: str | list):
    print(f"{choice!r}") # "Value 1", "Value 2" or [3, "Yes, it's an array"]
```

Inside `on_choice`, you receive exactly what you defined in `choices`: a string, list, number, function — anything.

**Callback keyboard** — each button calls its own method:

```py
self.chain.set_inline_keyboard({
    "« Back": self.display_previous_page,
    "Next »": self.display_next_page,
})
```

Useful for pagination, navigation, or menus.

### Command Parameters

Telekit can parse and validate command parameters for you.

```py
from telekit.parameters import *

class GreetHandler(telekit.Handler):
    @classmethod
    def init_handler(cls) -> None:
        cls.on.command("greet", params=[Int(), Str()]).invoke(cls.handle)

    def handle(self, age: int | None = None, name: str | None = None):
        if age is None or name is None:
            self.chain.sender.set_text("Usage: /greet <age> <name>")
        else:
            self.chain.sender.set_text(f"Hello, {name}! You are {age} years old. Next year you'll turn {age + 1} 😅")
        self.chain.send()
```

Now `/greet 64 "Alice Reingold"` or `/greet 128 Dracula` are parsed automatically.

> [!TIP]
> If arguments are invalid or missing, you simply receive `None` and decide how to respond.

### Dialogue

Dialogs are built as a chain of steps. Each method waits for the user before continuing.

```py
class DialogueHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        cls.on.text("hello", "hi", "hey").invoke(cls.handle_hello)

    def handle_hello(self) -> None:
        self.chain.sender.set_text("👋 Hello! What is your name?")
        if self.user.first_name:
            self.chain.set_entry_suggestions([self.user.first_name])
        self.chain.set_entry_text(self.handle_name)
        self.chain.send()

    def handle_name(self, name: str) -> None:
        self.user_name = name
        self.chain.sender.set_text("Nice! How are you feeling today?")
        self.chain.set_entry_text(self.handle_feeling)
        self.chain.send()

    def handle_feeling(self, feeling: str) -> None:
        self.chain.sender.set_text(f"Got it, {self.user_name.title()}! You feel: {feeling}")
        self.chain.set_inline_keyboard({"↺ Restart": self.handle_hello})
        self.chain.send()
```

How it works:

- The handler reacts to "hello", "hi", or "hey" (lowercase, UPPERCASE, or mixed).
- `handle_hello` asks for the user's name.
- `set_entry_suggestions` attaches the user's Telegram `first_name` as a suggestion button.
- `handle_name` stores the name in `self.user_name`.
- `handle_feeling` completes the flow and adds a `"↺ Restart"` button that routes back to the beginning.

It looks like regular Python. And reads like it too.

### Styles

Telekit lets you describe formatting as objects instead of writing raw HTML or Markdown.

```py
from telekit.styles import *

def handle(self) -> None:
    self.chain.sender.set_text(
        Bold("Text style examples:\n"),
        Stack(
            Bold("Bold text"),
            Italic("Italic text"),
            Bold(Italic("Bold + italic")),
            Link("Link", url="https://example.com"),
            BotLink("Deep link", username="MyBot", start="promo_42"),
            start="- {{index}}. ",
            sep=".\n",
        )
    )
    self.chain.send()
```

You describe structure. Telekit generates HTML or MarkdownV2 automatically:

```html
<b>Text style examples:</b>

- 1. <b>Bold text</b>.
- 2. <i>Italic text</i>.
- 3. <b><i>Bold + italic</i></b>.
- 4. <a href="https://example.com">Link</a>.
- 5. <a href="https://t.me/MyBot?start=promo_42">Deep link</a>
```

No manual escaping. No broken formatting because of one missing character.

### Telekit DSL

If you prefer not to write dialog logic in Python, you can use the built-in DSL with Jinja support.

```py
import telekit

class QuizHandler(telekit.TelekitDSL.Mixin):
    @classmethod
    def init_handler(cls) -> None:
        cls.analyze_string(script)
        cls.on.command("start").invoke(cls.start_script)

script = """
$ timeout {
    time = 20; // 20 sec.
}

@ main {
    title   = "🎉 Fun Facts Quiz";
    message = "Test your knowledge with 10 fun questions!";

    buttons {
        next("Start Quiz");
    }
}

@ question_1 {
    title   = "🐶 Question 1";
    message = "Which animal is the fastest on land?";
    buttons {
        _lose("Elephant");
        next("Cheetah");       // correct answer
        _lose("Horse");
        _lose("Lion");
    }
}

/* ... */
"""

telekit.Server(BOT_TOKEN).polling()
```

The DSL lets you describe scenarios as structured blocks:

- Scene-based architecture
- Anonymous scenes
- Automatic navigation stack management
- Link buttons
- Input handling
- Template variables
- Custom variables
- Hooks (Python API integration)
- Jinja template engine

You can find a [full quiz example](https://github.com/Romashkaa/telekit/blob/main/docs/examples/quiz.md) and [DSL reference](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/11_telekit_dsl.md) in the repository.

### Example Bot

You can launch an example bot by **running the following code**:

```py
import telekit

telekit.example(YOUR_BOT_TOKEN)
```

It includes example commands, dialogs, keyboards, and style usage.

## Why Telekit

- No FSM — just **chains**.
- Declarative, behavior-focused bot logic with minimal boilerplate.
- Automatic **callback routing** and **input handling**.
- **Styles API** for rich text (`Bold`, `Italic`, `Links`) with **automatic escaping**.
- Deep linking and **typed command parameters**.
- **Built-in DSL** for menus, FAQs, and simple bots.
- Seamless integration with **pyTelegramBotAPI**.

Telekit doesn't try to be everything.  
It tries to make Telegram bot development easier.

> [!TIP]
> If you're interested and want to learn more, check out the [Tutorial](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/0_tutorial.md)