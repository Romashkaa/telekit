# FAQ (Obsidian Canvas)

This example demonstrates how to build a simple multi-scene FAQ bot using **[Obsidian Canvas](../tutorial2/canvas/basics.md)**.

The handler loads a `.canvas` file, registers the `/start` command, and opens the topmost node as the first scene.

> `main.py`:
```py
import telekit

class CanvasHandler(telekit.DSLHandler):
    @classmethod
    def init_handler(cls) -> None:
        cls.analyze_canvas(CANVAS_PATH)
        cls.on.command("start").invoke(cls.start_script)

CANVAS_PATH: str = telekit.utils.read_canvas_path("canvas_path.txt")
TOKEN: str = telekit.utils.read_token("bot_token.txt")

telekit.Server(TOKEN).polling()
```

Before running, make sure you have:

- [Created a canvas](../tutorial2/canvas/setup_canvas.md)
- [Filled it with content](../tutorial2/canvas/basics.md)
- `canvas_path.txt` — containing the path to your `.canvas` file
- `bot_token.txt` — containing your bot token

> `.canvas` file:

<table> <tr>
    <td><img src="/docs/images/canvas/example6.png" alt="Canvas Example 6" width="500"></td>
</tr> </table>

> [!TIP]
> For a complete overview of Canvas mode, see the [Canvas tutorial](../tutorial2/canvas/contents.md).