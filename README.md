![TeleKit](https://github.com/Romashkaa/images/blob/main/TeleKitWide.png?raw=true)

[![PyPI](https://img.shields.io/pypi/v/telekit.svg)](https://pypi.org/project/telekit/)
[![Python](https://img.shields.io/pypi/pyversions/telekit.svg)](https://pypi.org/project/telekit/)

# Telekit

**Telekit** is a declarative, developer-friendly library for building Telegram bots. It gives developers a dedicated Sender for composing and sending messages and a Chain for handling dialogue between the user and the bot. The library also handles inline keyboards and callback routing automatically, letting you focus on the bot's behavior instead of repetitive tasks.

```py
import telekit

class MyBotHandler(telekit.Handler):
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

## Example Bot

You can launch an example bot with a wide range of demonstration commands by **running the following code**:

```py
import telekit

telekit.example(YOUR_BOT_TOKEN)
```

> [!TIP]
> If you're interested and want to learn more, check out the [Tutorial](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial2/0_tutorial.md)