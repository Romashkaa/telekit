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
    def init_handler(cls, bot: telebot.TeleBot) -> None:
        """
        Initializes the command handler.
        """
        @bot.message_handler(commands=['entry'])
        def handler(message: telebot.types.Message) -> None:
            cls(message).handle()

    # ------------------------------------------
    # Handling Logic
    # ------------------------------------------

    def handle(self) -> None:
        self._user_data = UserData(self.message.chat.id)
        self.input_name()

    def input_name(self, message: telebot.types.Message | None=None) -> None:
        prompt: telekit.Chain = self.get_child()
        prompt.set_always_edit_previous_message(True) # `chain.send()` will change the previous message instead of sending a new one
         
        prompt.sender.set_title("⌨️ What`s your name?")
        prompt.sender.set_message("Please, send a text message")

        name: str | None = self._user_data.get_name( # from own data base
            default=self.user.get_username() # from telebot API
        )
        
        if name:
            prompt.set_entry_suggestions([name])

        @prompt.entry_text(delete_user_response=True)
        def _(message: telebot.types.Message, name: str) -> None:
            confirm: telekit.Chain = self.get_child()

            confirm.sender.set_title(f"👋 Bonjour, {name}!")
            confirm.sender.set_message(f"Is that your name?")

            self._user_data.set_name(name)

            confirm.set_inline_keyboard(
                {
                    "« Change": prompt,
                    "Yes »": self.input_age,
                }, row_width=2
            )

            confirm.send() # Actually edits prompt message (REASON: prompt.set_always_edit_previous_message(True))

        prompt.send() # Sends new message

    def input_age(self, message: telebot.types.Message) -> None:
        prompt: telekit.Chain = self.get_child() # Child of `input_name.<locals>.confirm` (previous chain object)
         
        prompt.sender.set_title("⏳ How old are you?")
        prompt.sender.set_message("Please, send a numeric message")

        @prompt.entry_text(
            filter_message=lambda message, text: text.isdigit() and 0 < int(text) < 130,
            delete_user_response=True)
        def _(message: telebot.types.Message, text: str) -> None:
            confirm: telekit.Chain = self.get_child()

            confirm.sender.set_title(f"😏 {text} years old?")
            confirm.sender.set_message(f"Noted. Now I know which memes are safe to show you")
            self._user_data.set_age(int(text))

            confirm.set_inline_keyboard(
                {
                    "« Change": prompt,
                    "Ok »": self.result,
                }, row_width=2
            )

            confirm.send() # Actually edits prompt message

        prompt.send() # Actually edits previous message

    def result(self, message: telebot.types.Message) -> None:
        result: telekit.Chain = self.get_child() # Child of `input_age.<locals>.confirm` (previous chain object)
         
        result.sender.set_title("😏 Well well well")
        result.sender.set_message(f"So your name is {self._user_data.get_name()} and you're {self._user_data.get_age()}? Fancy!")

        result.set_inline_keyboard({"« Change": self.input_name})

        result.send() # Actually edits previous message