import telekit

class Test(telekit.DSLHandler):
    @classmethod
    def init_handler(cls) -> None:
        cls.analyze_canvas(CANVAS_PATH)
        cls.on.command("start").invoke(cls.start_script)

CANVAS_PATH: str = telekit.utils.read_canvas_path()
TOKEN: str = telekit.utils.read_token()

telekit.Server(TOKEN).polling()
