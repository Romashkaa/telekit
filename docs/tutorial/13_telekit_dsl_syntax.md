# Telekit DSL Syntax

## Content

- [Our first scene](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#our-first-scene)
- [Let’s add another scene](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#lets-add-another-scene)
- [Back Magic Scene](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#back)
- [Other Scene`s Attributes](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#other-scenes-attributes)
- [Links](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#links)
- [Configuration Block](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#configuration-block)
    - [Named Configuration Block](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#named-configuration-block)
- [Timeouts](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#timeout)
- [Multiline Strings](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#multiline-strings)
- [Buttons Without Label](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#buttons-without-label)
- [Next Magic Scene](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#next)
- [Template Variables](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#template-variables)
    - [Available Variables](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#available-variables)
    - [Custom Static Variables](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#custom-static-variables)
    - [Custom Dynamic Variables](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#custom-dynamic-variables)
    - [Default Values](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#default-values)
    - [Variable Resolution Order](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#variable-resolution-order)
- [Calling Python Methods in DSL](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#calling-python-methods-in-dsl)
    - [Argument Data Types](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#argument-data-types)
    - [Hook Types](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#hook-types)
- [Handling Text Input](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#handling-text-input)
- [Handoff Button](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#handoff-button)
- [Redirect Button](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#redirect-button)
- [Jinja Template Engine](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#jinja-extended-template-engine)
- [Additional Documentation](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#additional-documentation)
- [Examples](https://github.com/Romashkaa/telekit/blob/main/docs/examples/examples.md#telekit-dsl)

## Our first scene

Each Telekit DSL script starts with the main block (also called the main "scene"). This is the entry point (start) of the script:

```js
@ main {
    // Attributes
}
```

Next, we define the mandatory attributes for each scene, `title` and `message` - alogically with a standard telekit:

```js
@ main {
    title   = "📖 FAQ - Frequently Asked Questions";
    message = "Here are answers to common questions to help you get started:";
}
```

If we now load this code using the methods shown on the [Telekit DSL Integration](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/12_telekit_dsl_integration.md) page, we’ll see the message: 
> <b>📖 FAQ - Frequently Asked Questions</b>
>
> Here are answers to common questions to help you get started:

## Let’s add another scene

```js
@ main {
    title   = "📖 FAQ - Frequently Asked Questions";
    message = "Here are answers to common questions to help you get started:";
}

@ devs {
    title   = "👨‍💻 Telekit Developers";
    message = "Only me, Romashka :]";
}
```

And of course, we need to add buttons to switch between scenes:

```js
@ main {
    title   = "📖 FAQ - Frequently Asked Questions";
    message = "Here are answers to common questions to help you get started:";
    buttons {
        devs("👨‍💻 Developers");    // Opens @devs
    }
}

@ devs {
    title   = "👨‍💻 Telekit Developers";
    message = "Only me, Romashka :]";
    buttons {
        main("« Back");          // Opens @main
    }
}
```

Now we have two pages and the ability to switch between them.

But there’s one important problem...

## Back

Imagine we have a scene that can be accessed from two different places — the question is, how do we go back?

```js
@ main {
    ...
    buttons {
        devs("👨‍💻 Developers");     // Opens @devs
        docs("📚 Documentation");  // Opens @docs
    }
}

@ devs {
    ...
    buttons {
        main("« Back");      // Opens @main
        docs("Next »");      // Opens @docs
    }
}

@ docs {
    ...
    buttons {
        /*????*/("« Back");          // Opens what?
    }
}
```

For such cases, there’s a special magic scene called `back`.

The magic scene `back` automatically determines the previous scene using a LIFO stack.

Let’s rewrite the previous example using `back`:

```js
@ main {
    ...
    buttons {
        devs("👨‍💻 Developers");     // Opens @devs
        docs("📚 Documentation");  // Opens @docs
    }
}

@ devs {
    ...
    buttons {
        back("« Back");    // Opens @main
        docs("Next »");    // Opens @docs
    }
}

@ docs {
    ...
    buttons {
        back("« Back");      // Opens @main or @devs (using a LIFO stack)
    }
}
```

Perfect! Let’s move on.

## Other Scene`s Attributes

You can use the following attributes for any scene, like `@main`:

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
    parse_mode = "html" // (html | markdown) default: none

    //      ↓ button row width: `buttons(row_width)`
    buttons(2) { // default: 1    ↑↑↑↑↑↑↑↑↑
        devs("👨‍💻 Developers"); docs("📚 Docs");
    }
}
```

## Links

The `link()` button type is used to open external resources directly from the bot interface.

Unlike scene navigation buttons, a `link()` button **does not trigger a scene transition** and does not affect the navigation stack.

```js
buttons {
    link("Telekit", "https://github.com/Romashkaa/telekit")
}
```

- **Label** — text displayed on the button  
- **URL** — the external link that will be opened when the button is pressed

The user remains in the current scene after clicking a `link()` button.

> [!WARNING]
> This name is reserved and cannot be used as a scene name.

## Configuration Block

Configuration block starting with $ is used for global configuration.
Unlike scenes (@), configuration block don’t create a UI — it just set parameters for the whole script.

```js
$ {
    // set timeout (for example)
    timeout_time    = 10; // disabled by default
    timeout_message = "Are you still here?";
    timeout_label   = "Yes, i'm here";
}
```

### Named Configuration Block

You can also save time by creating a named block:

```js
$ timeout {
    time    = 10;
    message = "Are you still here?";
    label   = "Yes, i'm here";
}
```

## Timeout

Timeouts help prevent unnecessary memory usage when a user stops interacting with your bot for a long period of time.  
So, you can configure a timeout that clears all callbacks associated with a chat after a specified period of inactivity:

```js
$ timeout {
    time = 10; // 10 seconds
}
```

But before clearing the callbacks, the bot must confirm that the user is really inactive.
So when the timeout expires, it will first show a confirmation message:

```js
$ timeout {
    time    = 10;
    message = "Are you still here?"; // optional
    label   = "Yes, i'm here";       // optional
}
```

If the user clicks the "Yes, I’m here" button, they will continue from where they left off.

> [!NOTE]
> By default, the `message` and `label` are already set to "Are you still here?" and "Yes, I'm here".

## Multiline Strings

If you need to write a long text, you can use multiline strings with backticks ("`"):

```js
@ devs {
    title   = "👨‍💻 Telekit Developers";
    message = `
        Only me, Romashka :]
        And nobody else.
    `;
}
```

The Telekit parser automatically normalizes indentation in multiline strings.  

- The minimal common leading whitespace from all lines is removed.
- Leading and trailing empty lines are automatically trimmed.

For example:

```js
message = `
    - Home Tasks:
        - Task 1.
        - Task 2.
    - Watchlist:
        - Movie 1.
`;
```

Will be transformed into:

```js
- Home Tasks:
    - Task 1.
    - Task 2.
- Watchlist:
    - Movie 1.
```

## Buttons Without Label

In Telekit DSL, you can create buttons without explicitly specifying a label.
The button will automatically use the scene’s default label if provided, or fall back to the scene’s title

```js
@ main {
    title   = "📖 FAQ - Frequently Asked Questions";
    message = "Here are answers to common questions to help you get started:";
    buttons {
        developers;    // "Who are developers" - scene's default label
        documentation; // "📚 Documentation" - fall back to the scene's title
    }
}

// default label ↓
@ developers("Who are developers") {
    title   = "👨‍💻 Developer";
    message = "This bot was spellcrafted by [Telekit Wizard](https://t.me/+WsZ1SyGYSoI3YWQ8) 🪄✨";
}

@ documentation {
// fall back to the title ↓
    title   = "📚 Documentation";
    message = "Here you can find helpful guides and references.";
}
```

If you want a custom label, use parentheses with the text:

```js
buttons {
    developers("👨‍💻 Devs");
    documentation("📚 Docs");
}
```

> [!NOTE]
> `scene_name;` and `scene_name();` are equivalent

## Next

When building a linear bot, it can get tedious to repeatedly type out button labels. Here’s a look at how you can use the magic next scene:

```js
@ main {
    title   = "🧪 Quick Science Quiz";
    message = "Test your knowledge with these 3 fun questions!";

    buttons {
        next("Start Quiz");
    }
}

@ _lose { // ignored by `next` when determining scene order
    title   = "❌ Wrong Answer!";
    message = "Oops! That was not correct. Don't worry, you can try again.";

    buttons {
        back("« Try Again")  // redirect back to the quiz start
    }
}

@ question_1 {
    title   = "🌍 Question 1";
    message = "What is the largest planet in our Solar System?";
    buttons {
    //  question_2("Jupiter")  // without `next` you’d have to write it like this
        next("Jupiter");       // correct answer
        _lose("Earth");        // incorrect
        _lose("Mars");         // incorrect
        _lose("Venus");        // incorrect
    }
}

@ question_2 {
    title   = "🧬 Question 2";
    message = "Which gas do plants absorb from the atmosphere during photosynthesis?";
    buttons {
        _lose("Oxygen");         // incorrect
        next("Carbon Dioxide");  // correct answer
        _lose("Nitrogen");       // incorrect
        _lose("Hydrogen");       // incorrect
    }
}

@ question_3 {
    title   = "⚛️ Question 3";
    message = "What particle in an atom has a positive charge?";
    buttons {
        _lose("Electron");   // incorrect
        _lose("Neutron");    // incorrect
        _end("Proton");      // correct answer
        _lose("Photon");     // incorrect
    }
}

@ _end {
    title   = "🎉 Quiz Complete!";
    message = "You've finished the Science Quiz. Great job! 🌟\n\nWant to try again?";

    buttons {
        main("↺ Restart Quiz");
    }
}
```

- `next` moves to the following scene based on the order of scenes in the file, **skipping all scenes whose names begin with `_`**.
- Scenes that start with `_` are **ignored by `next`** and won’t be included in the linear sequence.
- You can override the default ordering using `next_order`:
```js
$ next {
    order = [
        question_2,
        question_1,
        question_3,
        _end // if you include underscore-scenes manually, they’ll be processed too
    ]
}
```
- You can change default `next` button label:
```js
$ next {
    label = "Next »";
}
```

> See the [full example](https://github.com/Romashkaa/telekit/blob/main/docs/examples/quiz.md)

## Template Variables

As your bot grows, you’ll often want messages to feel more personal instead of being fully static.  
For example, greeting a user by name or referencing their username.

Telekit DSL supports **template variables** using double curly braces: `{{variable}}`.

These variables can be used directly inside title, message, and button label fields.

```js
@ main {
    title   = "Welcome, {{first_name}}!";
    message = "Your username is {{username}}.";
    buttons {
        back("« {{prev_scene_name}}")
    }
}
```

- Variables are replaced **at render time**, right before the message is sent.
- Only **first-level substitution** is performed.
    - Variables inside variable values are **not** processed again.
    - This prevents infinite recursion and keeps rendering safe from injecting.
- All variable values are **automatically sanitized**:
    - HTML and Markdown inside variable values are escaped.
    - This prevents accidental formatting issues and injection problems.
    - Formatting must always be written explicitly in the DSL:
```js
message = "Your username is <b>{{username}}</b>";
parse_mode = "html";
```

### Available Variables

You can use the following variables in your Telekit DSL scripts to personalize messages:

- `{{first_name}}` – the first name of the user as provided by Telegram.  
- `{{last_name}}` – the last name of the user as provided by Telegram.  
- `{{full_name}}` – the full name of the user (first name + last name).  
- `{{username}}` – the Telegram username of the user (with the `@` symbol).
- `{{user_id}}` – the unique Telegram ID of the user.
- `{{prev_scene_name}}` – internal name of the previous scene (the identifier after @)
- [See more here](https://github.com/Romashkaa/telekit/blob/main/docs/documentation/telekit_dsl.md#available-variables)

### Custom Static Variables

In addition to the built-in template variables like `{{first_name}}` or `{{username}}`, Telekit allows you to define **your own variables directly in the DSL script**. 

These **static variables** are defined in a named `$ vars` configuration block and can store strings, numbers, or lists:

```js
$ vars {
    PRICE = 99
    AMENITIES = ["Wi-Fi", "Breakfast", "Parking"]
}
```

> [!NOTE]  
> Variables defined in a named `$ vars` block are equivalent to creating individual entries in the unnamed configuration block with the same values. For example, `$ vars { PRICE = 99 }` is similar to having a `$ { vars_PRICE = 99 }` in the unnamed configuration block.  
> See [Named Configuration Blocks](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#named-configuration-block) for more details.

When used in a template, lists and other non-string values are automatically converted to strings:

```js
title = "{{AMENITIES}}" // title = '["Wi-Fi", "Breakfast", "Parking"]'
```

### Custom Dynamic Variables

In addition to the static `$ vars`, Telekit DSL lets you define **dynamic variables** whose values are determined at runtime in python. This allows you to add **dynamic, personalized content** to your messages.

Custom variables are resolved by implementing the `get_variable` method in your handler class:

```python
import random

class QuizHandler(telekit.TelekitDSL.Mixin):
    ...
    def get_variable(self, name: str) -> str | None:
        match name:
            case "random_lose_phrase":
                phrases = [
                    "Keep going, you're doing great!",
                    "Don't give up!",
                    "Almost there, try again!",
                ]
                return random.choice(phrases)
            case _:
                return None
```

Then in your DSL script, you can reference the custom variable just like a built-in one:

```js
@ _lose {
    title   = "❌ Wrong Answer!";
    message = "Oops! {{random_lose_phrase}}"; // here

    buttons {
        back("« Retry");
    }
}
```

[See the full example](https://github.com/Romashkaa/telekit/blob/main/docs/examples/custom_variables.md)

Each time a user hits a wrong answer, the `random_lose_phrase` variable is dynamically chosen, making the quiz experience more engaging.

### Default Values

If a variable is missing or has no value (for example, `{{last_name}}` for a user who has not set a last name), you can provide a default value using the `:` syntax:

```js
@ main {
    title = "Hello, {{first_name:User}}!";
    message = "Welcome, {{last_name:there}}!";
}
```

- In this example, if `first_name` is missing, it will use `"User"` as a fallback.  
- If `last_name` is missing, it will use `"there"` as a fallback.  

This ensures that your messages always display meaningful text even when some user data is unavailable.

### Variable Resolution Order

When Telekit DSL evaluates a template variable, it follows a specific order to determine its value:

1. **Static variables** defined in the script inside a `$ vars` block.  
2. **Custom dynamic variables** provided by the handler via the `get_variable` method.  
3. **Built-in Telekit variables** such as `first_name`, `username`, etc.  
4. **Default values** specified directly in the template using the `{{variable:default}}` syntax.  

This order ensures that user-defined values override built-in defaults, while fallback defaults are applied only when no other value is found.

## Calling Python Methods in DSL

After seeing how template variables personalize messages, Telekit DSL goes one step further: it lets you **invoke python `Handler` methods directly from your script**. This means you can not only read and display values, but also trigger actions, update variables, or implement custom logic while the user interacts with your script.

Using hooks like `on_enter`, specify the name of the method you want to call and optionally pass arguments:

```js
@ throne_room {
    title = "🏰 Castle Ending 1"
    message = "You claim the throne. Victory!"
    
    on_enter {
        add_ending("throne_room")
    }
}
```

Each time this scene is displayed (either via a direct link, or using `back` or `next`), the `add_ending` method of the `QuestHandler` object will be called with the parameter `ending_name="throne_room"`:

```py
class QuestHandler(telekit.TelekitDSL.Mixin):
    @classmethod
    def init_handler(cls) -> None:
        cls.on.message(commands=["start"]).invoke(cls.handle)
        cls.analyze_source(script)

    def handle(self):
        self.visited_endings = set()
        self.start_script()

    def add_ending(self, ending_name: str):
        """API method called from DSL on_enter to mark an ending visited"""
        self.visited_endings.add(ending_name)
```

[See the full working example](https://github.com/Romashkaa/telekit/blob/main/docs/examples/python_api.md)

### Argument Data Types

When calling Python methods from DSL hooks, you can pass arguments of the following types:

- none `none` – represents a `None` value in Python (case-insensitive)
- bool `true` / `false` – boolean values (case-insensitive)
- numbers `21` / `3.14` – integers or floats
- strings `"August"` – text values
- lists `[21, ["telekit"]]` – arrays containing any combination of the above types

**Example:**
```js
on_enter {
    save_purchase(["Laptop", "Headphones", "Mouse"], 1299.99)
}
```

You can also use variables directly in hook arguments:

```js
on_enter {
    my_method("Hello {{username}}")
}
```

> [!IMPORTANT]  
> Template variables are only substituted **when passed directly as a string**.  
> They will **not** be evaluated if placed inside a list or nested inside other data structures.  

**Example:**

```js
on_enter {
    my_method("Hello {{username}}")   // works
    my_method(["Hello {{username}}"]) // variables will not be replaced
}
```

### Hook Types

A scene can have multiple hooks, each triggered at a specific moment during the scene's lifecycle:

- `on_enter` – triggered **every time** the scene is entered (either via a direct link, or using `back` or `next`)
- `on_enter_once` – triggered **only the first time** the scene is entered (either via a direct link, or using `back` or `next`)
- `on_exit` — triggered after the scene message has been sent
- `on_timeout` — triggered when a configured timeout fires due to user inactivity
- [See more here](https://github.com/Romashkaa/telekit/blob/main/docs/documentation/telekit_dsl.md#hook-types-python-api)

These hooks let you perform dynamic actions, update variables, or trigger custom logic directly from your DSL script.

You can combine multiple hooks and method calls in a single scene:

```js
on_enter_once {
    add_ending("treasure_found")
    log_event("Entered treasure_room")
    award_points("gold", 100)
}
on_enter {
    save_progress // save user state to database
}
```

> [!NOTE] 
> Method arguments are optional — you can leave the parentheses empty or omit them entirely

## Handling Text Input

Starting from version 1.7.0, Telekit allows you to **react to text entered by the user** and manage scene transitions based on this input without additional Python code.

```js
entries {
    scene_name("text") // scene to open when the user entered "text"
    default_scene_name // default scene to open if the entered value does not match any listed
}
```

- `"text"` - the specific text value expected from the user.
- `scene_name` — scene to open when the user entered that text.  
- `default_scene_name` — scene to open if the entered value does not match any specified values.

> [!NOTE]
> `buttons { ... }` and `entries { ... }` do not conflict. You can freely use them together, especially in combination with the feature explained in the "Input Suggestions" section.

### Capturing Input

You can access the text entered by the user through the `{{entry}}` variable and use its value within the scene's message, title, button labels, or even as arguments when calling functions.

```js
@ main {
    title = "Welcome!"
    message = "Enter the text:"

    // triggers `correct` when the user enters anything
    entries { print() }
}

@ print {
    title = "Printing..."
    message = "You entered: {{entry}}"
    buttons { back() }
}
```

- In this example, the `entries { print() }` block captures **any text entered by the user**.  
- When the user types something, the `print` scene is opened, and the `{{entry}}` variable contains exactly what the user typed.  
- The message in the `print` scene shows the entered text using `{{entry}}`.

```js
@ main {
    title = "Welcome!"
    message = "Enter the password:"

    // button
    buttons { correct("Skip »") } // the `{{entry}}` variable in @correct will be `none`
    // triggers `correct` when the user enters "1111"
    entries { correct("1111") }   // the `{{entry}}` variable in @correct will be `"1111"`
}

@ correct {
    title = "Correct!"
    message = "You entered: {{entry:Nothing, you just clicked 'Skip'}}"
    buttons { back() }
}
```

- If the user enters "1111", the `correct` scene is opened and the `{{entry}}` variable contains the value `"1111"`.
- If the user clicks the "Skip" button, `{{entry}}` has no value (`none`). You can provide a default using `{{entry:DEFAULT}}` to handle such cases.

> [!IMPORTANT] 
> This is not "the last input": `{{entry}}` stores **only the value entered immediately before transitioning to this scene**.

### Input Suggestions

Telekit allows you to provide **suggested input values** to users via the `suggest()` button.  
These suggestions can be clicked to fill the input field and open the scene, making it easier for users to provide expected responses without typing everything manually.

```js
buttons {
    suggest("Label", "Value")
}
```

- **Label** — text displayed on the button  
- **Value** — input value that will be passed to `{{entry}}` variable

```js
buttons {
    suggest("1111") // label == value
}
```

- If only one argument is provided, the button label is automatically set to the same value.

> [!TIP]
> Check the [example](https://github.com/Romashkaa/telekit/blob/main/docs/examples/password.md) for a complete demonstration of how to use input handling.

## Handoff Button

The `handoff` button is equivalent to the same method in the handler. It allows you to seamlessly switch control to another handler.

```js
@ main {
    title = "📚 Telekit DSL Examples"
    message = `
        Explore DSL examples step by step — from simple to advanced.
        Use the buttons below to try them out:
    `
    buttons {
        handoff("🤔 Quiz", "QuizHandler")
    }
}
```

> [!NOTE] 
> `handoff("🤔 Quiz", "QuizHandler")` in the script is equivalent to `self.handoff("QuizHandler").handle()` in code

## Redirect Button

The `redirect` button simulates the user sending a specific message or command when clicked:

```js
@ main {
    title = "📚 Telekit DSL Examples"
    message = `
        Explore DSL examples step by step — from simple to advanced.
        Use the buttons below to try them out:
    `
    buttons {
        redirect("Quiz", "/quiz") // send command `/quiz`
        redirect("Pricing", "/faq pricing") // send the command `/faq` with the argument `pricing`
        redirect("Say hello to the Bot", "Hello, bot!") // send the message: "Hello, bot!"
    }
}
```

> [!NOTE] 
> Clicking a `redirect` button automatically ends the current script. Therefore, the value is **not passed** to `entries { ... }` in the scene.

## Jinja: Extended Template Engine

Telekit DSL supports **Jinja** as an alternative and more powerful template engine.
It allows you to use **conditions, loops, expressions, and filters** directly inside DSL fields.

Jinja is useful when simple `{{variable}}` substitution is not enough.

```js
@ cart {
    title = "🛒 Rooms in your cart:"
    message = `
        {% for room in handler.cart -%}
            {{ room.title() }}
        {% endfor %}
    `
    template = "jinja"
    buttons { rooms("Book more »") }
}
```

> [!NOTE]  
> This tutorial does not cover Jinja syntax in detail.  
> Please refer to the [official Jinja documentation](https://jinja.palletsprojects.com/en/stable/templates/) for full syntax and features.

### Activation

You can enable Jinja **globally** using a configuration block:

```js
$ {
    template = "jinja"
}
```

Or enable it **locally per scene**:

```js
@ main {
    ...
    template = "jinja"
}
```

### Context

Telekit automatically injects several objects into the Jinja context:

- `{{ handler }}` — the current handler instance
  - Example: `{{ handler.user.first_name or "no name" }}`
- All static variables defined in `$ vars { ... }`
  - Example: `{{ PRICE }}`

### Custom Context

You can override existing variables or add new ones using the `set_jinja_context` method.

- Example 1 (keyword arguments):
```py
def handle(self):
    self.set_jinja_context(
        name="value"
    )
    self.start_script()
```

- Example 2 (dictionary-based context):
```py
def handle(self):
    self.set_jinja_context(
        {
            "name": "value"
        }
    )
    self.start_script()
```

A context value can be **any Python object**, including functions.

> [!TIP]
> Check the [example](https://github.com/Romashkaa/telekit/blob/main/docs/examples/jinja_engine.md)

## Additional Documentation

- [Additional Documentation](https://github.com/Romashkaa/telekit/blob/main/docs/documentation/telekit_dsl.md) ⭐️
    - [Data types](https://github.com/Romashkaa/telekit/blob/main/docs/documentation/telekit_dsl.md#data-types)
    - [Scene's attributes](https://github.com/Romashkaa/telekit/blob/main/docs/documentation/telekit_dsl.md#scenes-attributes)
    - [Configuration attributes](https://github.com/Romashkaa/telekit/blob/main/docs/documentation/telekit_dsl.md#configuration-attributes)
    - [Magic scenes](https://github.com/Romashkaa/telekit/blob/main/docs/documentation/telekit_dsl.md#magic-scenes)
    - [Available variables](https://github.com/Romashkaa/telekit/blob/main/docs/documentation/telekit_dsl.md#available-variables)
    - [Variable resolution order](https://github.com/Romashkaa/telekit/blob/main/docs/documentation/telekit_dsl.md#variable_resolution_order)
    - [Hook types (Python API)](https://github.com/Romashkaa/telekit/blob/main/docs/documentation/telekit_dsl.md#hook-types-python-api)
    - [Suggested Emojis for Buttons](https://github.com/Romashkaa/telekit/blob/main/docs/documentation/telekit_dsl.md#suggested-emojis-for-buttons)

---

The parser and analyzer provide an excellent system of warnings and errors with examples, so anyone can figure it out!