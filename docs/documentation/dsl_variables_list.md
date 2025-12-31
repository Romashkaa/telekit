## Available Variables

You can use the following variables in your Telekit DSL scripts to personalize messages:

### Basic
- `first_name` – the first name of the user as provided by Telegram.  
- `last_name` – the last name of the user as provided by Telegram.  
- `full_name` – the full name of the user (first name + last name).  
- `username` – the Telegram username of the user (with the `@` symbol).
- `user_id` – the unique Telegram ID of the user.
- `chat_id` – the ID of the chat where the message originated.

### Context
- `prev_scene_name` – name of the previous scene
- `prev_scene_title` – title of the previous scene
- `prev_scene_message` – main text of the previous scene

### Technical
- `scene_ref_count` – number of scenes linking to the current scene
- `button_ref_count` – number of buttons pointing to the current scene

[« Back to tutorial](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#available-variables)