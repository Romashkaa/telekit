from . import guide_mixin

import telebot

class GuideKit:
    def __init__(self, source_path: str, on_commands: list[str]=["/help"]):
        self.source_path = source_path
        self.on_commands = on_commands

    def register(self):
        class DefaultGuideHandler(guide_mixin.GuideMixin):
            @classmethod
            def init_handler(cls) -> None:
                cls.on.message(self.on_commands).invoke(cls.start_guide, False)
                cls.analyze_file(self.source_path)

