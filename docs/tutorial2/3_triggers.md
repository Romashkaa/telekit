# Triggers

Each handler class has an `on` object that provides trigger methods such as `command`, який ми використали в минулому прикладі. These triggers listen for incoming updates from the server and initiate processing. 

Each handler may define multiple triggers:

```py
import telekit

class MyHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        cls.on.command("start").invoke(cls.handle)
        cls.on.text("Hola").invoke(cls.handle)
        cls.on.photo().invoke(cls.handle)
        cls.on.regexp(r"^hi|hello|hey$").invoke(cls.handle)
        cls.on.message(content_types=["document"]).invoke(cls.handle)

    def handle(self):
        self.chain.sender.set_text("Hello!")
        self.chain.send()

telekit.Server(BOT_TOKEN).polling() # start your bot
```

Click to expand for details:
<details>
<summary><b>command</b> trigger</summary>

Used to listen for specific commands sent by the user. You can specify one or more command strings that the handler should react to:

```py
cls.on.command("start", "greet").invoke(cls.handle)
```
</details>

<details>
<summary><b>text</b> trigger</summary>

Used to listen for specific text messages. The matching is case-sensitive, and you can provide multiple text options to listen for:

```py
cls.on.text("Hola", "hola").invoke(cls.handle)
```

<details>
<summary><b>photo</b> trigger</summary>

Used to listen for messages containing photos:

```py
cls.on.photo().invoke(cls.handle)
```
</details>

<details>
<summary><b>regexp</b> trigger</summary>

Used to listen for text messages that match a given regular expression pattern:

```py
cls.on.regexp(r"^hi|hello|hey$").invoke(cls.handle)
```
</details>

<details>
<summary><b>message</b> trigger</summary>

Used as a general-purpose trigger that matches messages based on various criteria. It extends the original trigger functionality from PyTelegramBotAPI with extra features.

```py
# 1. Trigger on videos only
cls.on.message(content_types=["video"]).invoke(cls.handle)

# 2. Trigger on audio messages in private chats
cls.on.message(content_types=["audio"], chat_types=["private"]).invoke(cls.handle)

# 3. Trigger only for specific users (whitelist)
cls.on.message(whitelist=[123456789, 987654321]).invoke(cls.handle)

# 4. Trigger with a custom filter function
cls.on.message(func=lambda message: len(message.text or "") > 100).invoke(cls.handle)

# 5. Trigger on messages matching a regex pattern
cls.on.message(regexp=r"^Hello|Hi there!$").invoke(cls.handle)
```
</details>


## Filters

<details>
<summary>Whitelist Filter</summary>
Used to restrict who the trigger responds to:

```py
cls.on.command("admin", whitelist=[123456789]).invoke(cls.handle)
```
</details>

<details>
<summary>Chat Types Filter</summary>
Used to restrict which chats the trigger responds to:

```py
cls.on.command("admin", chat_types=['private']).invoke(cls.handle)
```

Available chat types:
- `private` - Private chat
- `group` - Group chat
- `supergroup` - Supergroup
- `channel` - Channel
</details>

## Message Object

To access a sent photo or document, you can use `self.message` — this is the message sent by the user that triggered the handler.

todo:
Params for commands
Params for texts