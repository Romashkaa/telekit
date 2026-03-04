# QR Generator

Simple QR code generator with an interactive editor. On `/start`, the bot displays a default QR code and lets the user customize it:

- edit the encoded text
- add a caption 

All without leaving the chat!

> `main.py` file:

```py
from typing import Any

import telekit
from telekit.styles import Quote


class QRCode:
    def __init__(self) -> None:
        self.text:    str | None = None
        self.caption: str | None = None

    def get_url(self) -> str:
        kwargs: dict[str, Any] = {"text": self.text or "Example"}
        if self.caption is not None:
            kwargs["caption"] = self.caption
        return telekit.utils.make_qrcode(**kwargs)


class QRHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        cls.on.command("start").invoke(cls.handle)

    def handle(self) -> None:
        self.qrcode = QRCode()
        self.display_qrcode()

    # ── entry points ──────────────────────────────────────────────

    def change_text(self) -> None:
        self.chain.sender.set_title("⌨️ Enter text")
        self.chain.sender.set_message("Send any text or URL to encode into a QR code")
        self.chain.set_entry_text(self.set_text, delete_user_response=True)

        keyboard: dict[str, Any] = {}
        keyboard["« Back"] = self.display_qrcode

        if self.qrcode.text:
            keyboard["✕ Remove"] = self.set_text

        self.chain.set_inline_keyboard(keyboard, row_width=2)
        self.chain.edit()

    def change_caption(self) -> None:
        self.chain.sender.set_title("⌨️ Enter caption")
        self.chain.sender.set_message("Send a caption to display below the QR code")
        self.chain.set_entry_text(self.set_caption, delete_user_response=True)

        keyboard: dict[str, Any] = {}
        keyboard["« Back"] = self.display_qrcode

        if self.qrcode.caption:
            keyboard["✕ Remove"] = self.set_caption

        self.chain.set_inline_keyboard(keyboard, row_width=2)
        self.chain.edit()

    # ── entry handlers ──────────────────────────────────────────────────

    def set_text(self, text: str | None = None) -> None:
        self.qrcode.text = text
        self.display_qrcode()

    def set_caption(self, caption: str | None = None) -> None:
        self.qrcode.caption = caption
        self.display_qrcode()

    # ── display QR code ───────────────────────────────────────────────────

    def display_qrcode(self) -> None:
        url: str = self.qrcode.get_url()

        self.chain.sender.set_photo(url)
        self.chain.sender.set_text(
            Quote(url, expandable=True),
            "Use the buttons below to edit the QR code:"
        )
        self.chain.set_inline_keyboard(
            {
                "✏️ Edit Text": self.change_text,
                "✏️ Edit Caption" if self.qrcode.caption else "➕ Add Caption": self.change_caption,
            },
            row_width=2
        )
        self.chain.edit()

TOKEN: str = telekit.utils.read_token()
telekit.Server(TOKEN).polling()
```