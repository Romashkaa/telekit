import telekit
from telekit.types import ButtonStyle, CallbackButton

class UserData:
    names: telekit.Vault = telekit.Vault(
        path             = "data_base", 
        table_name       = "names", 
        key_field_name   = "user_id", 
        value_field_name = "name"
    )
    
    ages: telekit.Vault = telekit.Vault(
        path             = "data_base", 
        table_name       = "ages", 
        key_field_name   = "user_id", 
        value_field_name = "age"
    )
    
    def __init__(self, chat_id: int):
        self.chat_id = chat_id

    def get_name(self, default: str | None=None) -> str | None:
        return self.names.get(self.chat_id, default)

    def set_name(self, value: str):
        self.names[self.chat_id] = value

    def get_age(self, default: int | None=None) -> int | None:
        return self.ages.get(self.chat_id, default)

    def set_age(self, value: int):
        self.ages[self.chat_id] = value

class EntryHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        """
        Initializes the command handler.
        """
        cls.on.command('entry').invoke(cls.handle)

    # ------------------------------------------
    # Handling Logic
    # ------------------------------------------

    def handle(self) -> None:
        self._user_data = UserData(self.message.chat.id)
        self.chain.disable_timeout_warnings()
        self.entry_name()

    # -------------------------------
    # NAME HANDLING
    # -------------------------------

    def entry_name(self) -> None:
        self.chain.sender.set_title("⌨️ What`s your name?")
        self.chain.sender.set_message("Please, send a text message")
        self.chain.sender.set_use_italics()

        self.chain.set_entry_text(self.handle_name, delete_user_response=True)

        # Priority:
        # 1. Previous response (internal database)
        # 2. Telegram username (fallback)
        name: str | None = self._user_data.get_name(
            default=self.user.username
        )
        
        if name:
            self.chain.set_entry_suggestions([name])

        self.chain.edit()

    def handle_name(self, name: str) -> None:
        self.chain.sender.set_title(f"👋 Bonjour, {name}!")
        self.chain.sender.set_message(f"Is that your name?")

        self._user_data.set_name(name)

        self.chain.set_inline_keyboard(
            {
                "« Change": CallbackButton(self.entry_name, style=ButtonStyle.DANGER),
                "Yes »": CallbackButton(self.entry_age, style=ButtonStyle.SUCCESS)
            }, row_width=2
        )

        self.chain.edit()

    # -------------------------------
    # AGE HANDLING
    # -------------------------------
    
    def entry_age(self) -> None:
        self.chain.sender.set_title("⏳ How old are you?")
        self.chain.sender.set_message("Please, send a numeric message")

        self.chain.set_entry_text(
            self.handle_age, 
            filter_message=lambda text: text.isdigit() and 0 < int(text) < 130,
            delete_user_response=True
        )

        age: int | None = self._user_data.get_age()

        if age:
            self.chain.set_entry_suggestions([str(age)])

        self.chain.edit()

    def handle_age(self, text: str) -> None:
        self._user_data.set_age(int(text))

        self.chain.sender.set_title(f"😏 {text} years old?")
        self.chain.sender.set_message("Noted. Now I know which memes you prefer")

        self.chain.set_inline_keyboard(
            {
                "« Change": CallbackButton(self.entry_age, style=ButtonStyle.DANGER),
                "Ok »": CallbackButton(self.show_result, style=ButtonStyle.SUCCESS),
            }, row_width=2
        )
        self.chain.edit()

    # ------------------------------------------
    # RESULT
    # ------------------------------------------

    def show_result(self):
        name = self._user_data.get_name()
        age = self._user_data.get_age()

        self.chain.sender.set_title("😄 Well well well")
        self.chain.sender.set_message(f"So your name is {name} and you're {age}? Fancy!")

        self.chain.set_inline_keyboard({
            "« No, change": CallbackButton(self.entry_name, style=ButtonStyle.DANGER),
        }, row_width=2)

        self.chain.edit()