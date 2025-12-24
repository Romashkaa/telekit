# Telekit DSL Syntax

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

---

Let’s add another scene:

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

## Other Scene`s Attributes:

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

## Configuration Block

Configuration block starting with $ is used for global configuration.
Unlike scenes (@), configuration block don’t create a UI — it just set parameters for the whole script.

```js
$ {
    // set global timeout (optional)
    timeout_time    = 10; // disabled by default
    timeout_message = "Are you still here?";
    timeout_label   = "Yes, i'm here";
}
```

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

---

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
        developers;    // "Who are developers"
        documentation; // "📚 Documentation"
    }
}

@ developers("Who are developers") {
    title   = "👨‍💻 Developer";
    message = "This bot was spellcrafted by [Telekit Wizard](https://t.me/+WsZ1SyGYSoI3YWQ8) 🪄✨";
}

@ documentation {
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

## Template Variables

As your bot grows, you’ll often want messages to feel more personal instead of being fully static.  
For example, greeting a user by name or referencing their username.

Telekit DSL supports **template variables** using double curly braces: `{{variable}}`.

These variables can be used directly inside `title` and `message` fields.

```js
@ main {
    title   = "Welcome, {{first_name}}!";
    message = "Your username is {{username}}.";
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
- `{{chat_id}}` – the ID of the chat where the message originated.

### Custom Variables

In addition to the built-in template variables like `{{first_name}}` or `{{username}}`, Telekit allows you to define **your own variables**.  

Custom variables are resolved by implementing the `get_variable` method in your handler class. When rendering a DSL script:  

1. The DSL engine encounters a `{{variable}}` in your script.  
2. It calls your handler’s `get_variable(name)` method:  
   - If it returns a string, that value replaces the variable.  
   - If it returns `None`, the engine uses the built-in variables instead.
   
This allows you to add **dynamic, personalized content** to your messages.

```python
...
import random

class FAQHandler(telekit.TelekitDSL.Mixin):
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

---

The parser and analyzer provide an excellent system of warnings and errors with examples, so anyone can figure it out!