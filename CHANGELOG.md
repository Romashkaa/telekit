# 1.2.0

## ✅ New Features
### Sender Improvements
- `set_document` method - sets a file object (any document) to be sent to the user.
- `set_text_as_document` method - converts text into a temporary document (BytesIO) and sets it for sending.
- `set_video` method - sets the video for the message.
- `set_video_note` method — sets a video note (round video) for the message.
- `set_animation` method - sets the animation for the message.
- `set_audio` method — sets an audio file (music) for the message.
- `set_voice` method — sets a voice message (OGG) for the message.
- `remove_attachments` method - clears all attachments from the message or object, resetting photo, media, and document
- `ChatAction` and `send_chat_action` for chat action support.

### Handler Improvements

### Chain Improvements

### DSL Improvements
- Added support for {{variables}} in `title=` and `message=`.
  - HTML and Markdown tags in variable values are automatically sanitized.
  - Recursive variable replacement is prevented (only first-level substitution is performed).
  - Example: (`<b>username</b>` - bold; `{{first_name}}` and `{{username}}` - sanitized>)
```js
@ main {
    title = "Welcome, {{first_name:user}}!"; // "user" is default value
    message = "Did you know your <b>username</b> is {{username}}? Cool, isn't it?";
    parse_mode = "html";
}
```
- Improved indentation handling in multiline strings.
- `display_script_data()` method. Prints the semantic model of the script to the console.
- Mixin refactor.

---

## ⏳ Delayed
- DSL warning for strings with too many buttons or excessive text  
- Localization support for `self.user.enable_logging()` (currently global)