## New Button Types

| **Name**             | **Description**                                          |
|----------------------|----------------------------------------------------------|
| `AlertButton`        | A callback button that shows a popup alert when pressed. |
| `NotificationButton` | A callback button that shows a notification.             |
| `InvokeButton`       | A callback button that calls the object method.          |

## User Improvements

| **Name**               | **Description**                                           |
| ---------------------- | --------------------------------------------------------- |
| `bio`                  | Bio of the user or description of the chat.               |
| `birthdate`            | Birthdate of the user, if set and visible.                |
| `description`          | Description of the group or channel.                      |
| `mention`              | `tg://user?id=` deep link, works even without a username. |
| `is_private`           | Whether the message was sent in a private chat.           |
| `is_group`             | Whether the message was sent in a group.                  |
| `is_supergroup`        | Whether the message was sent in a supergroup.             |
| `is_channel`           | Whether the message was sent in a channel.                |
| `avatar`               | File ID of the user's most recent profile photo.          |
| `profile_photos_count` | Total number of profile photos the user has set.          |

- Refactor: `User` now accepts a `Message` object instead of `chat_id` + `from_user`. All properties are derived from `_sender` (`from_user` or `chat`) and migrated to `cached_property`. Fixed broken `get_id` and `get_full_name` references.
- Added `__repr__`.

## Sender Improvements

| **Name**                   | **Description**                                        |
| -------------------------- | ------------------------------------------------------ |
| `sent_message`             | The last message sent by this sender instance.         |
| `disable_notification`     | Disables notification sound when the message is sent.  |
| `protect_content`          | Protects the message contents from forwarding and saving. |
| `reply_parameters`         | Reply parameters for the message to be sent.           |
| `link_preview_options`     | Link preview options for the message to be sent.       |
| `show_caption_above_media` | Shows the caption above the media instead of below.    |

- Refactored sending system.

## Chain Improvements

| **Name**    | **Description**                                              |
| ----------- | ------------------------------------------------------------ |
| `received`  | The message received from the user during entry processing.  |