import telekit

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

class HelpHandler(telekit.TelekitDSL.Mixin):
    @classmethod
    def init_handler(cls) -> None:
        cls.analyze_file(str(ROOT_DIR / "help.tsc"))
        cls.on.message(commands=["help"]).invoke(cls.handle)

    def handle(self):
        self.start_script()