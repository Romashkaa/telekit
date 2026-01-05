## DSL Improvements

Version 1.7.0 focuses on making the Telekit DSL more interactive, expressive, and convenient for building dialogs. This update adds user input handling capabilities and introduces link buttons.

The key improvement is the integration of the `entries { ... }` block, which allows reacting to text entered by the user and using that value in subsequent scenes. Along with this, the `{{entry}}` variable was introduced to store the entered value. The `suggest()` mechanism was also added, providing input suggestions that work seamlessly with entries.

The update introduces a new `link()` button type, which allows opening external resources directly from the bot interface.

Taken together, these changes make the Telekit DSL a more powerful tool for creating complex, yet readable and extensible scripts.

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

### Links

New `link("Label", "URL")` button type – creates a button that opens a link.  

```js
buttons {
    link("GitHub", "https://github.com/Romashkaa/telekit")
}
```

> [!NOTE]
> Unlike `scene()` or `suggest()`, a `link()` button **does not navigate to another scene**, it opens the external URL.

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