import telekit

class CanvasHandler(telekit.DSLHandler):
    @classmethod
    def init_handler(cls) -> None:
        cls.analyze_canvas(CANVAS_PATH)
        cls.on.command("start").invoke(cls.start_script)

CANVAS_PATH: str = telekit.utils.read_canvas_path(".env")
TOKEN: str = telekit.utils.read_token(".env")

telekit.Server(TOKEN).polling()
