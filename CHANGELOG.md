## Trigger Improvements

| **Name** | **Description** |
|----------|-----------------|
| `on.text` | *BugFix:* Commands are no longer matched as text triggers. |

- Internal refactor of the `On` class.

## New Utils

| **Name** | **Description** |
|----------|-----------------|
| `make_bot_link` | Builds a `t.me` URL to a bot with an optional deep-link payload. |
| `make_user_link` | Builds a `t.me` URL to a user with an optional pre-filled message. |
| `make_qrcode` | Generates a [QR code](./docs/examples/qr_gen.md) URL from any text or link. |