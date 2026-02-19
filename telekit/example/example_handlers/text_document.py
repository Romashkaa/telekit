from telebot.types import Message
from telekit.types import (
    TextDocument, CopyTextButton, ParseMode
)
from telekit.styles import Quote, Escape
import telekit
    
class TextDocumentHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        cls.on.command("entry_document").invoke(cls.handle)

    # ------------------------------------------
    # Handling Logic
    # ------------------------------------------

    def handle(self) -> None:
        self.entry_text_document()

    def entry_text_document(self) -> None:
        self.chain.sender.set_title("📄 Send text document...")
        self.chain.sender.set_message("Please, send a .txt, .md or .py document")

        self.chain.set_entry_text_document(
            self.handle_text_document,
            allowed_extensions=(".txt", ".py", ".md")
        )

        self.chain.disable_timeout_warnings()
        self.chain.edit()

    def handle_text_document(self, document: TextDocument):
        self.chain.sender.set_title(Escape(f"🔎 File ", repr(document.file_name), " info"))
        self.chain.sender.set_message(
            Quote(
                document.text[:64].strip(), 
                "..." if len(document.text) > 64 else ""
            ), "\n",
            f"• Encoding {document.encoding!r}\n",
            f"• Length {len(document.text)}\n",
            f"• Size {document.document.file_size}\n",
        )
        self.chain.set_inline_keyboard(
            {
                "Copy Name": CopyTextButton(document.file_name),
                "Resend ↺": self.entry_text_document
            }, row_width=2
        )
        self.chain.sender.set_parse_mode(ParseMode.HTML)
        self.chain.send()