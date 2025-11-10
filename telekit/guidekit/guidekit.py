from . import guide_mixin

import telebot

class GuideKit:
    def __init__(self, source_path: str, on_commands: list[str]=["/help"]):
        self.source_path = source_path
        self.on_commands = on_commands

    def register(self):
        class DefaultGuideHandler(guide_mixin.GuideMixin):
            @classmethod
            def init_handler(cls, bot: telebot.TeleBot) -> None:
                @cls.message_handler(self.on_commands)
                def handler(message: telebot.types.Message) -> None:
                    cls(message).start_guide()

                cls.analyze_file(self.source_path)

