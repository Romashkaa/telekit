import telebot.types # type: ignore
import telekit

pages: dict[str, tuple[str, str]] = {}

for title, text in telekit.chapters.read("help.txt").items():
    pages[title] = (title, text)

class HelpHandler(telekit.Handler):

    @classmethod
    def init_handler(cls, bot: telebot.TeleBot) -> None:
        """
        Initializes the command handler.
        """
        @bot.message_handler(commands=['help']) # type: ignore
        def handler(message: telebot.types.Message) -> None: # type: ignore
            cls(message).handle()

    # ------------------------------------------
    # Handling Logic
    # ------------------------------------------

    def handle(self) -> None:
        main: telekit.Chain = self.get_chain()
        main.set_always_edit_previous_message(True)
         
        main.sender.set_title("FAQ - Frequently Asked Questions")
        main.sender.set_message("Here are some common questions and answers to help you get started:")

        @main.inline_keyboard(pages)
        def _(message: telebot.types.Message, value: tuple[str, str]) -> None:
            page: telekit.Chain = self.get_child()

            page.sender.set_title(value[0])
            page.sender.set_message(value[1])

            page.set_inline_keyboard({"« Back": main})

            page.send()

        main.send()