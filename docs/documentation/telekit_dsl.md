# Telekit DSL Documentation

## Content

- [Data types](https://github.com/Romashkaa/telekit/blob/main/docs/documentation/telekit_dsl.md#data-types)
- [Scene's attributes](https://github.com/Romashkaa/telekit/blob/main/docs/documentation/telekit_dsl.md#scenes-attributes)
- [Configuration attributes](https://github.com/Romashkaa/telekit/blob/main/docs/documentation/telekit_dsl.md#configuration-attributes)
- [Hook types (python API)](https://github.com/Romashkaa/telekit/blob/main/docs/documentation/telekit_dsl.md#hook-types-python-api)
- [Magic scenes](https://github.com/Romashkaa/telekit/blob/main/docs/documentation/telekit_dsl.md#magic-scenes)
- [Available variables](https://github.com/Romashkaa/telekit/blob/main/docs/documentation/telekit_dsl.md#available-variables)
- [Variable resolution order](https://github.com/Romashkaa/telekit/blob/main/docs/documentation/telekit_dsl.md#variable_resolution_order)
- [Suggested emojis](https://github.com/Romashkaa/telekit/blob/main/docs/documentation/telekit_dsl.md#suggested-emojis-for-buttons)

## Data Types

When defining scene attributes, configuration values, or calling Python methods from DSL hooks, you can use literals of the following types:

- none `none` – represents a `None` value in Python (case-insensitive)
- bool `true` / `false` – boolean values (case-insensitive)
- numbers `21` / `3.14` – integers or floats
- strings `"August"` – text values
- lists `[21, ["telekit"]]` – arrays containing any combination of the above types

## Scene's Attributes

You can use the following attributes for any scene in Telekit DSL:

```js
@ main {
    // -- Required --

    title   = "Bold title text"
    message = "Regular text below"

    // -- Optional --

    // path to local file, URL, or Telegram file ID
    image = "path / reference / file_id"

    // enable or disable italics in message
    use_italics = false // default: false
    
    // change message parse mode
    parse_mode = "html" // (html | markdown) default: none

    //      ↓ button row width: `buttons(row_width)`
    buttons(2) { // default: 1    ↑↑↑↑↑↑↑↑↑
        devs("👨‍💻 Developers"); docs("📚 Docs")
    }

    // open a scene on a specific text
    entries { secret("1111") }

    // a hook called every time the scene is entered
    on_enter { method_name("arg") }
}
```

## Hook Types (Python API)

A scene can have multiple hooks, each triggered at a specific moment during the scene's lifecycle:

- `on_enter` – triggered **every time** the scene is entered (either via a direct link, or using `back` or `next`)
- `on_enter_once` – triggered **only the first time** the scene is entered (either via a direct link, or using `back` or `next`)
- `on_exit` — triggered after the scene message has been sent
- `on_timeout` — triggered when a configured timeout fires due to user inactivity

## Configuration Attributes

- `timeout_time` – specifies the timeout duration in seconds; if exceeded, the bot will clear callbacks associated with the chat. Disabled by default.  
- `timeout_message` – the message shown to the user when the timeout expires, asking for confirmation. Default: `"Are you still here?"`  
- `timeout_label` – the label for the button the user can click to confirm they are still active. Default: `"Yes, I'm here"`
- `next_order` – used to override the default sequence of scenes when using `next` buttons  
- `next_label` - optional, overrides the default label for `next` buttons. Default: `"Next »"`

## Magic Scenes

- [back](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#back) - returns the user to the previous scene using a LIFO stack.
- [next](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#next) - moves to the next scene based on the `next_order` config, which by default follows the order in the file, skipping scenes whose names start with `_`.

### Magic Non-Scenes

- `link(label, url)` — creates a button that opens an external URL directly from the bot without navigating to another scene.
- `suggest(label, suggestion)` — creates a button that provides a predefined input value and passes it to the `entries { ... }` handler as if the user typed it manually.

## Available Variables

You can use the following variables in your Telekit DSL scripts to [personalize messages](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#template-variables):

### Basic
- `first_name` – the first name of the user.  
  - `last_name` – the last name of the user.  
  - `full_name` – the full name of the user (first name + last name).  
- `username` – the Telegram username of the user (with the `@` symbol).
- `user_id` – the unique Telegram ID of the user.
- `chat_id` – the ID of the chat where the message originated.

### Entries
- `entry` - the text value entered by the user (or provided via `suggest("suggestion")`) that triggered the transition through the `entries { ... }` block to the current scene.

### Context
- `scene_name` - internal name of the current scene (the identifier after @)
  - `scene_title` - title of the current scene
  - `scene_message` - message text of the current scene
- `prev_scene_name` – internal name of the previous scene
  - `prev_scene_title` – title of the previous scene
  - `prev_scene_message` – message text of the previous scene

### Technical
- `scene_ref_count` – number of scenes linking to the current scene
- `button_ref_count` – number of buttons pointing to the current scene

## Variable Resolution Order

When Telekit DSL evaluates a template variable, it follows a specific order to determine its value:

1. **Static variables** defined in the script inside a `$ vars` block.  
2. **Custom dynamic variables** provided by the handler via the `get_variable` method.  
3. **Built-in Telekit variables** such as `first_name`, `username`, etc.  
4. **Default values** specified directly in the template using the `{{variable:default}}` syntax.  

This order ensures that user-defined values override built-in defaults, while fallback defaults are applied only when no other value is found.

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
