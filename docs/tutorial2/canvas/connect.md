# Connecting Canvas to Your Bot

## Minimal Example

```python
import telekit

class CanvasHandler(telekit.DSLHandler):
    @classmethod
    def init_handler(cls) -> None:
        cls.analyze_canvas(CANVAS_PATH)
        cls.on.command("start").invoke(cls.start_script)

CANVAS_PATH: str = "path/to/my-bot/bot.canvas"
TOKEN: str = "BOT_TOKEN"

telekit.Server(TOKEN).polling()
```

That's it. When the user sends `/start`, the bot renders the first scene — the node with the highest position in your canvas.

## How It Works

`analyze_canvas()` reads your `.canvas` file and converts it into a dialog model at startup. From that point, Telekit handles all navigation automatically based on the arrows you've drawn.

> [!TIP]
> Use `read_token()` and `read_canvas_path()` helpers to avoid hardcoding paths and tokens in your code:
>
> ```python
> from telekit.utils import read_token, read_canvas_path
>
> TOKEN       = read_token("token.txt")
> CANVAS_PATH = read_canvas_path("canvas_path.txt")
> ```
>
> Put the active token on the first line of `token.txt`

[Next: Canvas Basics](./basics.md) – Node format, navigation flows, and best practices.
