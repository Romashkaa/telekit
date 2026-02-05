## Chain Improvements
- ...

## Handler Improvements
- Add new trigger:
    - `func`

## Fixed Bugs
- Fixed a bug that caused `text`, `photo`, and similar handlers to behave as “one-time” triggers. Previously, while an active chain was waiting for its `timeout`, all incoming messages were only checked for commands. Only a command could interrupt the current chain — any other messages were ignored. As a result, triggers (for example, on the message `"hello"`) could effectively fire only once. This behavior has now been corrected: new messages are processed properly, and triggers work reliably without a one-time limitation.

## Planned:
- Add new triggers:
    - [x] func
    - [ ] document
    - [ ] text_document