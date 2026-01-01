## DSL Improvements

- Added static {{variables}} in DSL scripts:
```js
$ vars {
    PRICE = 90
    lower = "case too"
    any   = ["non-string", "values are converted to strings at compose time"]
}

@ room_21 {
    title = "🔑 Room 21"
    message = `
        Room 21 offers a comfortable bed, private bathroom,
        and everything you need for a quiet stay.

        🏷️ Price: $ {{PRICE}} per night
    `
}
```

- Added support using `{{variables}}` inside button labels and hook arguments:
```js
@ main {
    title = "hello"
    message = "hola"

    buttons {
        back("« {{prev_scene_name}}")
    }

    on_enter {
        add_to_busket("number:{{scene_name}}")
    }
}
```

- Added new built-in variables:
    - `scene_name` - internal name of the current scene (the identifier after @)
    - `scene_title` - title of the current scene
    - `scene_message` - message text of the current scene

- Added new Hooks:
    - `on_exit` — triggered after the scene message has been sent
    - `on_timeout` — triggered when a configured timeout fires due to user inactivity

- v1.6.1 Added new examples