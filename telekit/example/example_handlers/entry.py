import telebot.types
import telekit

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
        cls.on.message(commands=['entry']).invoke(cls.handle)

        # Or define the handler manually:

        # @cls.on.message(commands=['entry'])
        # def handler(message: telebot.types.Message) -> None:
        #     cls(message).handle()

    # ------------------------------------------
    # Handling Logic
    # ------------------------------------------

    def handle(self) -> None:
        self._user_data = UserData(self.message.chat.id)
        self.entry_name()

    # -------------------------------
    # NAME HANDLING
    # -------------------------------

    # The message parameter is optional, 
    # but you can receive it to access specific information
    def entry_name(self, message: telebot.types.Message | None=None) -> None:
        self.chain.sender.set_title("⌨️ What`s your name?")
        self.chain.sender.set_message("Please, send a text message")

        self.add_name_listener()

        name: str | None = self._user_data.get_name( # from own data base
            default=self.user.username # from telebot API
        )
        
        if name:
            self.chain.set_entry_suggestions([name])

        self.chain.edit()

    def add_name_listener(self):
        @self.chain.entry_text(delete_user_response=True)
        def _(message: telebot.types.Message, name: str) -> None:
            self.chain.sender.set_title(f"👋 Bonjour, {name}!")
            self.chain.sender.set_message(f"Is that your name?")

            self._user_data.set_name(name)

            self.chain.set_inline_keyboard(
                {
                    "« Change": self.entry_name,
                    "Yes »": self.entry_age,
                }, row_width=2
            )

            self.chain.edit()

    # -------------------------------
    # AGE HANDLING
    # -------------------------------

    def entry_age(self, message: telebot.types.Message | None=None) -> None:
        self.chain.sender.set_title("⏳ How old are you?")
        self.chain.sender.set_message("Please, send a numeric message")

        self.add_age_listener()

        age: int | None = self._user_data.get_age()

        if age:
            self.chain.set_entry_suggestions([str(age)])

        self.chain.edit()

    def add_age_listener(self):
        @self.chain.entry_text(
            filter_message=lambda message, text: text.isdigit() and 0 < int(text) < 130,
            delete_user_response=True
        )
        def _(message: telebot.types.Message, text: str) -> None:
            self._user_data.set_age(int(text))

            self.chain.sender.set_title(f"😏 {text} years old?")
            self.chain.sender.set_message("Noted. Now I know which memes are safe to show you")

            self.chain.set_inline_keyboard(
                {
                    "« Change": self.entry_age,
                    "Ok »": self.show_result,
                }, row_width=2
            )
            self.chain.edit()

    # ------------------------------------------
    # RESULT
    # ------------------------------------------

    def show_result(self):
        name = self._user_data.get_name()
        age = self._user_data.get_age()

        self.chain.sender.set_title("😏 Well well well")
        self.chain.sender.set_message(f"So your name is {name} and you're {age}? Fancy!")

        self.chain.set_inline_keyboard({
            "« No, change": self.entry_name,
        }, row_width=2)

        self.chain.edit()