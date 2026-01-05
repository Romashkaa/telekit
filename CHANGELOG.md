## Improvements

```js
@ main {
    title = "Welcome!"
    message = "Enter the password:"

    buttons (2) {
        suggest("Help", "1111") // suggestion
        okay("Skip »")
    }

    entries {
        okay("1111") // on "1111" message
        fail // default
    }
}

@ okay {
    title = "Correct!"
    message = `
        You entered: {{entry:Nothing, you just clicked 'Skip'}}

        Your reward is the following link:
    `

    buttons (2) {
        back()
        link("Reward", "https://github.com/Romashkaa/telekit")
    }
}

@ fail {
    title = "Wrong password: {{entry}}!"
    message = "The password you entered is incorrect. Please try again."

    buttons {
        back("« Try again")
    }
}
```

### Entries

The `entries { ... }` block is used to handle values entered by the user in a scene. It allows you to define actions that occur depending on what the user typed.  

#### Example 

```js
entries {
    scene_name("text") // scene to open when the user entered "text"
    default_scene_name // default scene to open if the entered value does not match any listed
}
```

- `"text"` - the specific text value expected from the user.
- `scene_name` — scene to open when the user entered that text.  
- `default_scene_name` — scene to open if the entered value does not match any specified values.

#### Example 2

```js
entries {
    okay("1111") // if the user entered "1111", the @okay scene is invoked
    okay("idk")  // if the user entered "idk", the @okay scene is invoked
    fail         // all other cases lead to the @fail scene
}
```

### New Variable

- **`{{entry}}`** stores the **value the user typed** on the keyboard that **caused the transition to the current scene** via the `entries { ... }` block.
    - If the scene was opened **not via `entries`** (e.g., a button, `back`, `next`, `link`, etc.), `{{entry}}` **has no value**.
    - To safely handle this case, use the default form:  
    **`{{entry:DEFAULT}}`** — if the value is missing, `DEFAULT` will be used.
> [!IMPORTANT] This is not "the last input globally"
> `{{entry}}` stores **only the value entered immediately before transitioning to this scene**.

### Suggestions

The `suggest()` button type is used to provide a suggested input value for an `entries { ... }` handler.

```js
buttons {
    suggest("Help", "1111")
}
```

- **Label** — text displayed on the button  
- **Value** — input value that will be passed to `entries { ... }`

```js
buttons {
    suggest("1111") // label == value
}
```

- If only one argument is provided, the button label is automatically set to the same value.

> [!NOTE]  
> The `{{entry}}` variable will be updated with the value provided by the `suggest()` button.
