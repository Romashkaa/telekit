from telebot import TeleBot


class DebugLevel:
    NONE:      int = 0
    INFO:      int = 1
    DEBUG:     int = 2


class TelekitState:

    __bot: TeleBot

    @classmethod
    def _init(cls, bot: TeleBot) -> None:
        if hasattr(cls, "_TelekitState__bot"):
            raise RuntimeError("TelekitState is already initialized")

        cls.__bot = bot
        cls._update()

    @classmethod
    def _update(cls):
        cls.__info = cls.__bot.get_me()

    @classmethod
    def get_bot(cls) -> TeleBot:
        if not hasattr(cls, "_TelekitState__bot"):
            raise RuntimeError("TelekitState is not initialized")

        return cls.__bot
    
    @classmethod
    def is_premium(cls) -> bool:
        return cls.__info.is_premium or False