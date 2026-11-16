# Telekit RAM usage per waiting user

A user is "waiting" when a handler has run, a keyboard has gone out, and Telekit keeps the callbacks alive until the user responds. This report measures how much memory each waiting user costs.

**Summary:** Memory grows linearly at 12–13 KB per user. Telekit frees nothing unless the handler sets a timeout. The 10,000 and 100,000 figures extrapolate from two measurements, at 100 and 1,100 users.

## Results

| Users | RAM above baseline | Total process RAM (baseline + users) |
|---|---|---|
| 100 (measured) | +1.3 MB | ~47 MB |
| 1,100 (measured) | +14.4 MB | ~60 MB |
| 10,000 (extrapolated) | ≈ 125–135 MB | ≈ 170–180 MB |
| 100,000 (extrapolated) | ≈ 1.25–1.35 GB | ≈ 1.3–1.4 GB |

- **Baseline:** resident memory (RSS) of the idle process after `telekit.Server(...)` is created and before any user is simulated. It measured 45.9 MB.
- **RAM above baseline:** RSS growth caused by the simulated users (`RSS_now − baseline`).
- **Total process RAM:** `baseline + RAM above baseline`.
- **Extrapolated rows:** `users × 12.4–13.4 KB`, the per-user cost from the two measured stages, plus the baseline.

## Raw measurements

| Stage | New users | RSS before | RSS after 10 s wait | Δ RSS | Per user |
|---|---|---|---|---|---|
| 1 | 100 | 45.92 MB | 47.22 MB | +1.30 MB | 13.28 KB |
| 2 | 1,000 | 47.59 MB | 59.70 MB | +12.11 MB | 12.40 KB |
| Total | 1,100 | 45.92 MB (baseline) | 60.30 MB (final) | +14.38 MB | 13.38 KB |

Both stages cost almost the same per user, which fits a linear model.

## What Telekit retains per user

A `gc` object census after 1,100 users shows these counts:

| Object type | Count (1,100 users) | Per user |
|---|---|---|
| `telebot.types.InlineKeyboardButton` | 4,400 | 4 |
| `telekit._inline_buttons.AnswerButton._CallbackInvoker` | 2,200 | 2 |
| `telekit._chain.Chain` | 1,100 | 1 |
| `telekit.senders.Sender` | 1,100 | 1 |
| `telekit._input_handler.InputHandler` | 1,100 | 1 |
| `telekit._timeout.TimeoutHandler` | 1,100 | 1 |
| `telebot.types.InlineKeyboardMarkup` | 1,100 | 1 |
| `telebot.Handler` | 1,100 | 1 |
| `telebot.types.Message` / `Chat` | 1,101 each | 1 |

- The button callbacks keep the chain machinery alive. The `StartHandler` instances get collected.
- `CallbackQueryHandler.user_button_callbacks` holds one entry per `chat_id`: 1,100 entries with 2 callbacks each, one per `add_alert` button.
- The process ran 3 threads throughout. Telekit does not spawn a thread per waiting user.

## Cleanup behavior

Without timeouts, memory scales with every user who has interacted with the bot since the last restart. Concurrent activity does not matter.

## Methodology

- **Version:** `2.6.0a5`. **Python:** 3.13.7.
- For each user, the script called `StartHandler(message)` and then `handler.handle()`.
- The script replaced `telebot.apihelper._make_request` with a stub, so `chain.edit()` runs to completion without contacting Telegram. The stub recorded 100 + 1,000 `sendMessage` calls.
- `psutil` read process RSS after `gc.collect()`.
- Each stage waited 10 seconds after creating its users and logged RSS every second.
- Stage 2 added 1,000 new users on top of the 100 from stage 1.

The tested handler sends one message with a title, a text and an inline keyboard of 4 buttons (2 `add_alert`, 2 `add_link`) through `chain.edit()`.

[**Tested handler**](https://github.com/Romashkaa/telekit/blob/main/docs/templates/default/handlers/start.py)