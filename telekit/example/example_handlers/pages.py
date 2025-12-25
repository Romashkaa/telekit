import telebot.types
import telekit

source = """
# Title

Page text!

# Another Page

Text of another page
Ця сторінка довша...

Але не дуже)

# Another Page 2
You can write right under the title!
"""

pages: dict[str, tuple[str, str]] = {}

for title, text in telekit.chapters.parse(source).items():
    pages[title] = (title, text)

# Alternative:

# for title, text in telekit.chapters.read("pages.txt").items():
#     pages[title] = (title, text)

class PagesHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        """
        Initializes the command handler.
        """
        @cls.bot.message_handler(commands=['pages'])
        def handler(message: telebot.types.Message) -> None:
            cls(message).handle()

    # ------------------------------------------
    # Handling Logic
    # ------------------------------------------

    def handle(self) -> None:
        self.display_home_page()

    def display_home_page(self) -> None:
        # `self.user.enable_logging()` enable logging for this user or for additional user IDs.
        # If no arguments are passed, enables logging for this instance's chat_id.
        self.user.enable_logging()
        
        self.chain.sender.set_title("Simple Pages Example")
        self.chain.sender.set_message("Here are some common questions and answers to help you get started:")

        @self.chain.inline_keyboard(pages)
        def _(message: telebot.types.Message, page: tuple[str, str]) -> None:
            self.display_page(page)

        self.chain.edit()

    def display_page(self, page: tuple[str, str]):
        self.user.logger.info(f"User clicked: {page[0]}")

        self.chain.sender.set_title(page[0])
        self.chain.sender.set_message(page[1])

        self.chain.set_inline_keyboard({"« Back": self.display_home_page})
        self.chain.edit()