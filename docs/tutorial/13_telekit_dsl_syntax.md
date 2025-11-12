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
    message = "Here are some common examples to help you get started:";
}
```

If we now load this code using the methods shown on the Telekit DSL Syntax￼ page, we’ll see the message: 
> "<b>📖 FAQ - Frequently Asked Questions</b>\n\n<i>Here...</i>".

---

Let’s add another scene:

```js
@ main {
    title   = "📖 FAQ - Frequently Asked Questions";
    message = "Here are some common examples to help you get started:";
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
    message = "Here are some common examples to help you get started:";
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

---

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

The magic scene `back` automatically determines the previous scene using a FILO stack.

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
        back("« Back");      // Opens @main or @devs (using a FILO stack)
    }
}
```

Perfect! Let’s move on.

## Other Scene`s Attributes:

You can use the following attributes for any scene, including `@main` and `@timeout`:

```js
@ main {
    // -- Required --

    title   = "📖 FAQ - Frequently Asked Questions";
    message = "Here are some common examples to help you get started:";

    // -- Optional --

    // image file, URL, or reference ID
    image = "path / reference / file_id";

    // enable or disable italics in message
    use_italics = false; // default: false
    
    // change message parse mode
    parse_mode = "Markdown" // default: "Markdown"

    // button row width: `buttons[row_width]`
    buttons[2] { // default: 1    ↑↑↑↑↑↑↑↑↑
        devs("👨‍💻 Developers"); docs("📚 Docs");
    }
}
```

---

## Configuration Block

Block "config" starting with $ is used for global configuration.
Unlike scenes (@), configuration block don’t create a UI — it just set parameters for the whole script.

```js
$ config {
    // set global timeout
    timeout = 10; // disabled by default
}
```

## Timeout

The `@timeout` scene is a special (magic) scene that appears automatically after the specified timeout period.  
To enable it, define the timeout duration in seconds inside `$config`, and then create a `@timeout` scene.

```js
$ config {
    // set timeout time in seconds
    timeout = 10;
}

@ timeout {
    title   = "⏰ Timeout";
    message = "Send /faq again";
    // ... you can use any attributes except buttons
}
```

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

## Buttons Without Label

In Telekit DSL, you can create buttons without explicitly specifying a label.  
The button will automatically use the name of the scene as its text.

```js
@ main {
    title   = "📖 FAQ - Frequently Asked Questions";
    message = "Here are some common examples to help you get started:";
    buttons {
        Developers;      // uses scene name as label
        Documentation;   // uses scene name as label
    }
}

@ Developers {
    // ...
}

@ docs {
    // ...
}
```

If you want a custom label, use parentheses with the text:

```js
buttons {
    Developers("👨‍💻 Devs");
    docs("📚 Docs");
}
```

---

## End

The parser and analyzer provide an excellent system of warnings and errors with examples, so anyone can figure it out!