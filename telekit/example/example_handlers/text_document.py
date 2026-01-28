from telebot.types import Message
from telekit.types import TextDocument
from telekit.styles import Quote, Sanitize
import telekit
    
class TextDocumentHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        """
        Initializes the command handler.
        """
        cls.on.command("entry_document").invoke(cls.handle)

    # ------------------------------------------
    # Handling Logic
    # ------------------------------------------

    def handle(self) -> None:
        self.entry_text_document()

    # -------------------------------
    # NAME HANDLING
    # -------------------------------

    def entry_text_document(self) -> None:
        self.chain.sender.set_title("📄 Send text document...")
        self.chain.sender.set_message("Please, send a .txt, .md or .py document")

        self.chain.set_entry_text_document(
            self.handle_text_document,
            allowed_extensions=(".txt", ".py", ".md")
        )

        self.chain.disable_timeout_warnings()
        self.chain.edit()

    def handle_text_document(self, message: Message, response: TextDocument):
        self.chain.sender.set_title(Sanitize(f"🔎 File ", repr(response.file_name), " info"))
        self.chain.sender.set_message(
            Quote(
                response.text[:64].strip(), 
                "..." if len(response.text) > 64 else ""
            ), "\n",
            f"• Encoding {response.encoding!r}\n",
            f"• Length {len(response.text)}\n",
            f"• Size {response.document.file_size}\n",
        )
        self.chain.sender.set_parse_mode("html")
        self.chain.send()