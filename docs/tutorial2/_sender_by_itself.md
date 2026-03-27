
## Sending & Error Handling

<details>
<summary>send</summary>

Sends or edits the message, including management of temporary messages. Does **not** handle exceptions — any error will be raised:

```py
self.chain.sender.send()
```

> [!IMPORTANT]
> `self.chain.sender.send()` only sends the message itself. It does not handle inline keyboards or other interactions — for those, you should use `self.chain.send()` or `self.chain.edit()`!

</details>

<details>
<summary>try_send</summary>

Attempt to send the message, returning message OR exception:

```py
message, error = self.chain.sender.try_send()

if message:
    print(f"Message #{message.message_id} was sent")
else:
    print(f"Exception: {error}")
```

> Attempts to send the message with error handling. 

Returns: 
- `[Message, None]` on success
- `[None, Exception]` on failure

</details>

<details>
<summary>send_or_handle_error</summary>

Attempts to send the message with error handling. Returns `Message` if the message was sent successfully, or `None` if an error occurred:

```py
message: Message | None = self.chain.sender.send_or_handle_error()

if message:
    print(f"Message #{message.message_id} was sent successfully")
```

If an error occurs, an error message containing the **exception type and description** is automatically sent to the user:

```md
ApiTelegramException

A request to the Telegram API was unsuccessful. Error code: 400. Description: Bad Request: can't parse entities: Can't find end tag corresponding to start tag "b".
```

> [!IMPORTANT]
> `self.chain.sender.send_or_handle_error()` only sends the message itself. It does not handle inline keyboards or other interactions — for those, you should use `self.chain.send()` or `self.chain.edit()`


</details>