import telekit

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent


class HelpHandler(telekit.TelekitDSL.Mixin):
    @classmethod
    def init_handler(cls) -> None:
        cls.on.message(commands=["help"]).invoke(cls.start_script)
        cls.analyze_file(str(ROOT_DIR / "help.tsc"))