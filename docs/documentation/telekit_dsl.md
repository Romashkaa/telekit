# Telekit DSL Documentation

## Data Types

When defining scene attributes, configuration values, or calling Python methods from DSL hooks, you can use literals of the following types:

- none `none` – represents a `None` value in Python
- bool `true` / `false` – boolean values
- numbers `21` / `3.14` – integers or floats
- strings `"August"` – text values
- lists `[21, ["telekit"]]` – arrays containing any combination of the above types


## Scene's Attributes

You can use the following attributes for any scene in Telekit DSL:

```js
@ main {
    // -- Required --

    title   = "Bold title text";
    message = "Regular text below";

    // -- Optional --

    // path to local file, URL, or Telegram file ID
    image = "path / reference / file_id";

    // enable or disable italics in message
    use_italics = false; // default: false
    
    // change message parse mode
    parse_mode = "html"; // (html | markdown) default: none

    //      ↓ button row width: `buttons(row_width)`
    buttons(2) { // default: 1    ↑↑↑↑↑↑↑↑↑
        devs("👨‍💻 Developers"); docs("📚 Docs")
    }

    // hook called every time the scene is entered
    on_enter {
        method_name("arg")
    }

    // hook called only the first time the scene is entered
    on_enter_once {
        method_name("arg")
    }
}
```

## Configuration Attributes

- `timeout_time` – specifies the timeout duration in seconds; if exceeded, the bot will clear callbacks associated with the chat. Disabled by default.  
- `timeout_message` – the message shown to the user when the timeout expires, asking for confirmation. Default: `"Are you still here?"`  
- `timeout_label` – the label for the button the user can click to confirm they are still active. Default: `"Yes, I'm here"`
- `next_order` – used to override the default sequence of scenes when using `next` buttons  
- `next_label` - optional, overrides the default label for `next` buttons. Default: `"Next »"`

## Magic Scenes

- [back](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#back) - returns the user to the previous scene using a LIFO stack.
- [next](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#next) - moves to the next scene based on the `next_order` config, which by default follows the order in the file, skipping scenes whose names start with `_`.

## Available Variables

You can use the following variables in your Telekit DSL scripts to [personalize messages](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#template-variables):

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

## Suggested Emojis for Buttons

This is an set of nice emoji labels you can use for buttons in your bot:

```
« Back
  Next »
↺ Restart
  What ？
✓ Okay
```

Alternative arrows:
```
← Back
  Next →
```

Additional:
```
★ Starred
☆ Star

✓ Okay
✕ Cancel

⊕ Add
⊖ Remove
```

Feel free to adapt them for your own scenes.
