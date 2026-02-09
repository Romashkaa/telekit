# Ads

This example shows how to send an announcement to several chats and notify the admin about the result.

```python
import telekit

class AdHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        # Only Admin Command ↴          AdminID
        cls.on.command("ad", whitelist=[1489794]).invoke(cls.send_ad)

    def send_ad(self):
        # list of chat IDs to send the ad
        recipients: list[int] = [123456789, 987654321]
        recipient_count: int  = 0

        for chat_id in recipients:
            sender = self.chain.create_sender(chat_id)
            sender.set_title("⚠️ Attention!")
            sender.set_message("This is an important announcement.")
            sender.set_effect(self.chain.sender.Effect.FIRE)
            if sender.send_or_handle_error():
                recipient_count += 1

        # notify the admin
        self.chain.sender.set_title("✅ Success")
        self.chain.sender.set_message(f"Your ad has been sent to {recipient_count}/{len(recipients)} recipients.")
        self.chain.send()

telekit.Server(TOKEN).polling()
```