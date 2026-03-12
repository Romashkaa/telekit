## New Button Types

| **Name**             | **Description**                                          |
|----------------------|----------------------------------------------------------|
| `AlertButton`        | A callback button that shows a popup alert when pressed. |
| `NotificationButton` | A callback button that shows a notification.             |

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