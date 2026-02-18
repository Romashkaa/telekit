from telebot import TeleBot


class TelekitState:

    __bot: TeleBot

    @classmethod
    def init(cls, bot: TeleBot) -> None:
        if hasattr(cls, "_TelekitState__bot"):
            raise RuntimeError("TelekitState is already initialized")

        cls.__bot = bot

    @classmethod
    def get_bot(cls) -> TeleBot:
        if not hasattr(cls, "_TelekitState__bot"):
            raise RuntimeError("TelekitState is not initialized")

        return cls.__bot
    
    DEBUG: bool = False