## DSL Improvements

- Added new built-in variables:
    - `scene_name` - internal name of the current scene (the identifier after @)
    - `scene_title` - title of the current scene
    - `scene_message` - message text of the current scene

- Added new Hooks:
    - `on_exit` — triggered after the scene message has been sent
    - `on_timeout` — triggered when a configured timeout fires due to user inactivity


## Planned for v1.6.0

- Static {{variables}} in DSL scripts:
```js
$ vars {
    PRICE = "$ 90"
    lower = "case too"
    any   = ["non-", "string", "values are converted to strings at compose time"]
}
```
- Support using `{{variables}}` inside button labels and hook arguments:
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

- Add Docs:
    - new variables
    - new hooks
    - support using `{{variables}}` inside button labels and hook arguments 
    - static {{variables}} in DSL script