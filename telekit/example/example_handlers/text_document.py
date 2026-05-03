from telekit.types import (
    TextDocument, CopyTextButton, ParseMode
)
from telekit.styles import Quote, Escape
import telekit
    
class TextDocumentHandler(telekit.traits.TrackHandoffOrigin, telekit.Handler):

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
        self.chain.sender.set_message("Please, send a .txt, .md, .html or .py document")

        self.chain.set_entry_text_document(
            self.handle_text_document,
            allowed_extensions=(".txt", ".py", ".md", ".html")
        )
        self.chain.set_inline_keyboard(
            {
                "« Back": self.handoff_back_or("StartHandler")
            }
        )

        self.chain.disable_timeout_warnings()
        self.chain.edit()

    def handle_text_document(self, document: TextDocument):
        self.chain.sender.set_title(Escape(f"🔎 File ", repr(document.file_name), " info"))
        self.chain.sender.set_message(
            Quote(
                document.text[:64].strip(), 
                "..." if len(document.text) > 64 else ""
            ),
            f"• Encoding {document.encoding!r}",
            f"• Length {len(document.text)}",
            f"• Size {document.format_size}",
            sep="\n"
        )
        self.chain.set_inline_keyboard(
            {
                "File Name": CopyTextButton(document.file_name),
                "Resend ↺": self.entry_text_document
            }, row_width=2
        )
        self.chain.sender.set_parse_mode(ParseMode.HTML)
        self.chain.send()